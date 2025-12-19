using System;
using System.Collections.Generic;
using System.Text;
using Juleportal.Data;
using Juleportal.Modeller;
using Juleportal.Tjenester;
using Newtonsoft.Json;

namespace Juleportal.Kontrollere
{
    public class AutentiseringKontroller
    {
        private readonly DatabaseKontekst _database;
        private readonly SlumptallsgeneratorTjeneste _slumptallsgeneratorTjeneste;
        private readonly Sesjonstjeneste _sesjonstjeneste;
        private readonly string _flagg;

        public AutentiseringKontroller(DatabaseKontekst database, Sesjonstjeneste sesjonstjeneste, string flagg)
        {
            _database = database;
            _slumptallsgeneratorTjeneste = new SlumptallsgeneratorTjeneste();
            _sesjonstjeneste = sesjonstjeneste;
            _flagg = flagg;
        }

        public string Registrer(string epost, string passord)
        {
            var forespørselId = _slumptallsgeneratorTjeneste.GenererForespørselsId();

            if (string.IsNullOrWhiteSpace(epost) || string.IsNullOrWhiteSpace(passord))
            {
                return LagSvar(false, "E-post og passord er påkrevd", forespørselId);
            }

            var bruker = new Bruker
            {
                Epost = epost.ToLower(),
                PassordHash = DatabaseKontekst.HashPassord(passord),
                ErAdministrator = false
            };

            if (_database.OpprettBruker(bruker))
            {
                return LagSvar(true, "Bruker registrert! God jul! 🎄", forespørselId);
            }
            else
            {
                return LagSvar(false, "En bruker med denne e-posten eksisterer allerede", forespørselId);
            }
        }

        public string LoggInn(string epost, string passord)
        {
            var forespørselsId = _slumptallsgeneratorTjeneste.GenererForespørselsId();

            if (string.IsNullOrWhiteSpace(epost) || string.IsNullOrWhiteSpace(passord))
            {
                return LagInnloggingSvar(false, "E-post og passord er påkrevd", forespørselsId);
            }

            var bruker = _database.HentBrukerMedEpost(epost);

            if (bruker == null || bruker.PassordHash != DatabaseKontekst.HashPassord(passord))
            {
                return LagInnloggingSvar(false, "Ugyldig e-post eller passord", forespørselsId);
            }

            var token = _sesjonstjeneste.OpprettToken(epost, passord);

            return LagInnloggingSvar(true, "Velkommen! Ho ho ho! 🎅", forespørselsId, token, bruker.ErAdministrator);
        }

        public string GlemtPassord(string epost)
        {
            var forespørselId = _slumptallsgeneratorTjeneste.GenererForespørselsId();

            var tilbakestillingskode = _slumptallsgeneratorTjeneste.GenererTilbakestillingskode();
            if (string.IsNullOrWhiteSpace(epost))
            {
                return LagSvar(false, "E-post er påkrevd", forespørselId);
            }

            var bruker = _database.HentBrukerMedEpost(epost);

            if (bruker != null)
            {
                var utløper = DateTimeOffset.UtcNow.AddMinutes(15).ToUnixTimeSeconds();
                _database.OppdaterTilbakestillingskode(epost, tilbakestillingskode, utløper);
                // ÅGJØRE: Implementer epostutsending    
            }

            return LagSvar(true, "Hvis e-posten eksisterer, har vi sendt en tilbakestillingskode. Sjekk innboksen din! 📧🎁", forespørselId);
        }

        public string TilbakestillPassord(string epost, string kode, string nyttPassord)
        {
            var forespørselsId = _slumptallsgeneratorTjeneste.GenererForespørselsId();

            if (string.IsNullOrWhiteSpace(epost) || string.IsNullOrWhiteSpace(kode) || string.IsNullOrWhiteSpace(nyttPassord))
            {
                return LagSvar(false, "Alle felt er påkrevd", forespørselsId);
            }

            var bruker = _database.HentBrukerMedEpost(epost);
            var nå = DateTimeOffset.UtcNow.ToUnixTimeSeconds();

            if (bruker == null || bruker.Tilbakestillingskode != kode || 
                !bruker.TilbakestillingskodeUtloper.HasValue || 
                bruker.TilbakestillingskodeUtloper.Value < nå)
            {
                return LagSvar(false, "Ugyldig eller utløpt kode", forespørselsId);
            }

            _database.OppdaterPassord(epost, DatabaseKontekst.HashPassord(nyttPassord));
            return LagSvar(true, "Passord oppdatert! 🎄", forespørselsId);
        }

        public string HentFlagg(string autorisasjonsHeader)
        {
            var forespørselsId = _slumptallsgeneratorTjeneste.GenererForespørselsId();

            if (string.IsNullOrWhiteSpace(autorisasjonsHeader) || !autorisasjonsHeader.StartsWith("Bearer "))
            {
                return LagSvar(false, "Ikke autorisert", forespørselsId);
            }

            var token = autorisasjonsHeader.Substring("Bearer ".Length);
            var bruker = _sesjonstjeneste.ValiderToken(token);

            if (bruker == null)
            {
                return LagSvar(false, "Ugyldig token", forespørselsId);
            }

            if (!bruker.ErAdministrator)
            {
                return LagSvar(false, "Bare administratorer har tilgang til flagget! 🎅", forespørselsId);
            }

            var resultat = new Dictionary<string, object>
            {
                { "suksess", true },
                { "melding", "Ho ho ho! Her er flagget ditt! 🎅🎄" },
                { "forespørselsId", forespørselsId },
                { "flagg", _flagg }
            };
            return JsonConvert.SerializeObject(resultat);
        }

        private string LagSvar(bool suksess, string melding, string forespørselsId)
        {
            var svar = new Dictionary<string, object>
            {
                { "suksess", suksess },
                { "melding", melding },
                { "forespørselsId", forespørselsId }
            };
            return JsonConvert.SerializeObject(svar);
        }

        private string LagInnloggingSvar(bool suksess, string melding, string forespørselsId, string token = null, bool erAdmin = false)
        {
            var svar = new Dictionary<string, object>
            {
                { "suksess", suksess },
                { "melding", melding },
                { "forespørselsId", forespørselsId }
            };

            if (token != null)
            {
                svar["token"] = token;
                svar["erAdministrator"] = erAdmin;
            }

            return JsonConvert.SerializeObject(svar);
        }
    }
}
