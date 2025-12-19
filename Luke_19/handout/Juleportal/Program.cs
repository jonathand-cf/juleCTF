using System;
using System.IO;
using Juleportal.Data;
using Juleportal.Kontrollere;
using Juleportal.Tjenester;

namespace Juleportal
{
    class Program
    {
        static void Main(string[] args)
        {
            Console.WriteLine("🎄🎅 Nordpolens Juleportal starter... 🎅🎄");
            Console.WriteLine();

            var databasesti = Environment.GetEnvironmentVariable("DATABASE_STI") ?? "/data/juleportal.db";
            var nettsidesti = Environment.GetEnvironmentVariable("NETTSIDE_STI") ?? Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "nettside");
            var port = Environment.GetEnvironmentVariable("PORT") ?? "8080";
            var flagg = Environment.GetEnvironmentVariable("FLAGG") ?? "JUL{falskt_flagg}";

            var datamappe = Path.GetDirectoryName(databasesti);
            if (!string.IsNullOrEmpty(datamappe) && !Directory.Exists(datamappe))
            {
                Directory.CreateDirectory(datamappe);
            }

            var database = new DatabaseKontekst(databasesti);

            var sesjonstjeneste = new Sesjonstjeneste(database);

            var autentiseringKontroller = new AutentiseringKontroller(database, sesjonstjeneste, flagg);

            var url = $"http://*:{port}/";
            var tjener = new HttpTjener(url, autentiseringKontroller, nettsidesti);

            Console.WriteLine($"🎁 Flagg: {flagg}");
            Console.WriteLine();

            tjener.Start();
        }
    }
}
