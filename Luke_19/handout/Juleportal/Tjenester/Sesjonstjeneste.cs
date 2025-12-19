using System;
using System.Text;
using Juleportal.Data;
using Juleportal.Modeller;

namespace Juleportal.Tjenester
{
    public class Sesjonstjeneste
    {
        private readonly DatabaseKontekst _database;

        public Sesjonstjeneste(DatabaseKontekst database)
        {
            _database = database;
            Console.WriteLine("🔐 Sesjonstjeneste initialisert");
        }

        public string OpprettToken(string epost, string passord)
        {
            var tokenData = $"{epost}:{passord}";
            return Convert.ToBase64String(Encoding.UTF8.GetBytes(tokenData));
        }

        public Bruker ValiderToken(string token)
        {
            if (string.IsNullOrWhiteSpace(token))
                return null;

            try
            {
                var decoded = Encoding.UTF8.GetString(Convert.FromBase64String(token));
                var deler = decoded.Split(new[] { ':' }, 2);
                
                if (deler.Length != 2)
                    return null;

                var epost = deler[0];
                var passord = deler[1];

                var bruker = _database.HentBrukerMedEpost(epost);
                
                if (bruker == null)
                    return null;

                if (bruker.PassordHash != DatabaseKontekst.HashPassord(passord))
                    return null;

                return bruker;
            }
            catch
            {
                return null;
            }
        }
    }
}
