using System;
using System.Collections.Generic;
using System.Data.SQLite;
using System.IO;
using System.Security.Cryptography;
using System.Text;
using Juleportal.Modeller;

namespace Juleportal.Data
{
    public class DatabaseKontekst
    {
        private readonly string _tilkoblingsstreng;
        private static bool _erInitialisert = false;

        public DatabaseKontekst(string databasesti)
        {
            _tilkoblingsstreng = $"Data Source={databasesti};Version=3;";
            
            if (!_erInitialisert)
            {
                OpprettTabeller();
                LagAdminBruker();
                _erInitialisert = true;
            }
        }

        private void OpprettTabeller()
        {
            using (var tilkobling = new SQLiteConnection(_tilkoblingsstreng))
            {
                tilkobling.Open();
                
                var kommando = new SQLiteCommand(@"
                    CREATE TABLE IF NOT EXISTS Brukere (
                        Id INTEGER PRIMARY KEY AUTOINCREMENT,
                        Epost TEXT UNIQUE NOT NULL,
                        PassordHash TEXT NOT NULL,
                        ErAdministrator INTEGER DEFAULT 0,
                        Tilbakestillingskode TEXT,
                        TilbakestillingskodeUtloper INTEGER
                    )", tilkobling);
                
                kommando.ExecuteNonQuery();
            }
        }

        private void LagAdminBruker()
        {
            var adminEpost = "admin@nordpolen.jul";
            
            if (HentBrukerMedEpost(adminEpost) == null)
            {
                var adminPassord = Environment.GetEnvironmentVariable("ADMIN_PASSORD") ?? "ErAnnetPassordPåServeren!";
                
                var bruker = new Bruker
                {
                    Epost = adminEpost,
                    PassordHash = HashPassord(adminPassord),
                    ErAdministrator = true
                };
                
                OpprettBruker(bruker);
                Console.WriteLine("🎅 Admin-bruker opprettet: admin@nordpolen.jul");
            }
        }

        public Bruker HentBrukerMedEpost(string epost)
        {
            using (var tilkobling = new SQLiteConnection(_tilkoblingsstreng))
            {
                tilkobling.Open();
                
                var kommando = new SQLiteCommand(
                    "SELECT Id, Epost, PassordHash, ErAdministrator, Tilbakestillingskode, TilbakestillingskodeUtloper FROM Brukere WHERE Epost = @epost",
                    tilkobling);
                kommando.Parameters.AddWithValue("@epost", epost.ToLower());
                
                using (var leser = kommando.ExecuteReader())
                {
                    if (leser.Read())
                    {
                        return new Bruker
                        {
                            Id = Convert.ToInt32(leser["Id"]),
                            Epost = leser["Epost"].ToString(),
                            PassordHash = leser["PassordHash"].ToString(),
                            ErAdministrator = Convert.ToInt32(leser["ErAdministrator"]) == 1,
                            Tilbakestillingskode = leser["Tilbakestillingskode"]?.ToString(),
                            TilbakestillingskodeUtloper = leser["TilbakestillingskodeUtloper"] == DBNull.Value 
                                ? (long?)null 
                                : Convert.ToInt64(leser["TilbakestillingskodeUtloper"])
                        };
                    }
                }
            }
            
            return null;
        }

        public bool OpprettBruker(Bruker bruker)
        {
            try
            {
                using (var tilkobling = new SQLiteConnection(_tilkoblingsstreng))
                {
                    tilkobling.Open();
                    
                    var kommando = new SQLiteCommand(@"
                        INSERT INTO Brukere (Epost, PassordHash, ErAdministrator) 
                        VALUES (@epost, @passordHash, @erAdmin)",
                        tilkobling);
                    
                    kommando.Parameters.AddWithValue("@epost", bruker.Epost.ToLower());
                    kommando.Parameters.AddWithValue("@passordHash", bruker.PassordHash);
                    kommando.Parameters.AddWithValue("@erAdmin", bruker.ErAdministrator ? 1 : 0);
                    
                    kommando.ExecuteNonQuery();
                    return true;
                }
            }
            catch (SQLiteException)
            {
                return false;
            }
        }

        public void OppdaterTilbakestillingskode(string epost, string kode, long utloper)
        {
            using (var tilkobling = new SQLiteConnection(_tilkoblingsstreng))
            {
                tilkobling.Open();
                
                var kommando = new SQLiteCommand(@"
                    UPDATE Brukere 
                    SET Tilbakestillingskode = @kode, TilbakestillingskodeUtloper = @utloper 
                    WHERE Epost = @epost",
                    tilkobling);
                
                kommando.Parameters.AddWithValue("@kode", kode);
                kommando.Parameters.AddWithValue("@utloper", utloper);
                kommando.Parameters.AddWithValue("@epost", epost.ToLower());
                
                kommando.ExecuteNonQuery();
            }
        }

        public void OppdaterPassord(string epost, string nyttPassordHash)
        {
            using (var tilkobling = new SQLiteConnection(_tilkoblingsstreng))
            {
                tilkobling.Open();
                
                var kommando = new SQLiteCommand(@"
                    UPDATE Brukere 
                    SET PassordHash = @passord, Tilbakestillingskode = NULL, TilbakestillingskodeUtloper = NULL 
                    WHERE Epost = @epost",
                    tilkobling);
                
                kommando.Parameters.AddWithValue("@passord", nyttPassordHash);
                kommando.Parameters.AddWithValue("@epost", epost.ToLower());
                
                kommando.ExecuteNonQuery();
            }
        }

        public static string HashPassord(string passord)
        {
            using (var sha256 = SHA256.Create())
            {
                var bytes = sha256.ComputeHash(Encoding.UTF8.GetBytes(passord));
                return Convert.ToBase64String(bytes);
            }
        }
    }
}
