using System;
using System.Collections.Generic;
using System.IO;
using System.Net;
using System.Text;
using System.Threading;
using Juleportal.Kontrollere;
using Newtonsoft.Json;

namespace Juleportal
{
    public class HttpTjener
    {
        private readonly HttpListener _lytter;
        private readonly AutentiseringKontroller _autentiseringKontroller;
        private readonly string _nettsidesti;
        private bool _kjører;

        public HttpTjener(string url, AutentiseringKontroller autentiseringKontroller, string nettsidesti)
        {
            _lytter = new HttpListener();
            _lytter.Prefixes.Add(url);
            _autentiseringKontroller = autentiseringKontroller;
            _nettsidesti = nettsidesti;
        }

        public void Start()
        {
            _lytter.Start();
            _kjører = true;
            Console.WriteLine("🎄 Nordpolens Juleportal kjører!");
            Console.WriteLine($"📍 Lytter på: {string.Join(", ", _lytter.Prefixes)}");

            while (_kjører)
            {
                try
                {
                    var kontekst = _lytter.GetContext();
                    ThreadPool.QueueUserWorkItem((_) => HåndterForespørsel(kontekst));
                }
                catch (HttpListenerException)
                {
                    break;
                }
            }
        }

        public void Stopp()
        {
            _kjører = false;
            _lytter.Stop();
        }

        private void HåndterForespørsel(HttpListenerContext kontekst)
        {
            var forespørsel = kontekst.Request;
            var respons = kontekst.Response;

            try
            {
                var sti = forespørsel.Url.AbsolutePath;
                
                Console.WriteLine($"[{DateTime.Now:HH:mm:ss}] {forespørsel.HttpMethod} {sti}");

                if (sti.StartsWith("/api/"))
                {
                    HåndterApi(forespørsel, respons);
                }
                else
                {
                    HåndterStatiskFil(sti, respons);
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Feil: {ex.Message}");
                SendFeil(respons, 500, "Intern serverfeil");
            }
            finally
            {
                respons.Close();
            }
        }

        private void HåndterApi(HttpListenerRequest forespørsel, HttpListenerResponse respons)
        {
            var sti = forespørsel.Url.AbsolutePath.ToLower();
            var metode = forespørsel.HttpMethod;

            respons.ContentType = "application/json; charset=utf-8";

            string resultat = null;

            if (metode == "POST")
            {
                var kropp = LesKropp(forespørsel);
                var data = JsonConvert.DeserializeObject<Dictionary<string, string>>(kropp) ?? new Dictionary<string, string>();

                switch (sti)
                {
                    case "/api/autentisering/registrer":
                        resultat = _autentiseringKontroller.Registrer(
                            HentVerdi(data, "epost"),
                            HentVerdi(data, "passord"));
                        break;

                    case "/api/autentisering/logginn":
                        resultat = _autentiseringKontroller.LoggInn(
                            HentVerdi(data, "epost"),
                            HentVerdi(data, "passord"));
                        break;

                    case "/api/autentisering/glemt-passord":
                        resultat = _autentiseringKontroller.GlemtPassord(
                            HentVerdi(data, "epost"));
                        break;

                    case "/api/autentisering/tilbakestill-passord":
                        resultat = _autentiseringKontroller.TilbakestillPassord(
                            HentVerdi(data, "epost"),
                            HentVerdi(data, "kode"),
                            HentVerdi(data, "nyttPassord"));
                        break;
                }
            }
            else if (metode == "GET")
            {
                switch (sti)
                {
                    case "/api/autentisering/flagg":
                        var authHeader = forespørsel.Headers["Authorization"];
                        resultat = _autentiseringKontroller.HentFlagg(authHeader);
                        break;
                }
            }

            if (resultat != null)
            {
                SendJson(respons, resultat);
            }
            else
            {
                SendFeil(respons, 404, "Endepunkt ikke funnet");
            }
        }

        private void HåndterStatiskFil(string sti, HttpListenerResponse respons)
        {
            if (sti == "/" || sti == "")
            {
                sti = "/index.html";
            }

            var filsti = Path.Combine(_nettsidesti, sti.TrimStart('/'));

            if (File.Exists(filsti))
            {
                var innhold = File.ReadAllBytes(filsti);
                respons.ContentType = HentInnholdstype(filsti);
                respons.ContentLength64 = innhold.Length;
                respons.OutputStream.Write(innhold, 0, innhold.Length);
            }
            else
            {
                SendFeil(respons, 404, "Fil ikke funnet");
            }
        }

        private string LesKropp(HttpListenerRequest forespørsel)
        {
            using (var leser = new StreamReader(forespørsel.InputStream, forespørsel.ContentEncoding))
            {
                return leser.ReadToEnd();
            }
        }

        private string HentVerdi(Dictionary<string, string> data, string nøkkel)
        {
            return data.ContainsKey(nøkkel) ? data[nøkkel] : null;
        }

        private void SendJson(HttpListenerResponse respons, string json)
        {
            var buffer = Encoding.UTF8.GetBytes(json);
            respons.ContentLength64 = buffer.Length;
            respons.OutputStream.Write(buffer, 0, buffer.Length);
        }

        private void SendFeil(HttpListenerResponse respons, int statuskode, string melding)
        {
            respons.StatusCode = statuskode;
            respons.ContentType = "application/json; charset=utf-8";
            
            var feil = JsonConvert.SerializeObject(new { feil = melding });
            var buffer = Encoding.UTF8.GetBytes(feil);
            respons.ContentLength64 = buffer.Length;
            respons.OutputStream.Write(buffer, 0, buffer.Length);
        }

        private string HentInnholdstype(string filsti)
        {
            var utvidelse = Path.GetExtension(filsti).ToLower();
            switch (utvidelse)
            {
                case ".html": return "text/html; charset=utf-8";
                case ".css": return "text/css; charset=utf-8";
                case ".js": return "application/javascript; charset=utf-8";
                case ".json": return "application/json; charset=utf-8";
                case ".png": return "image/png";
                case ".jpg":
                case ".jpeg": return "image/jpeg";
                case ".gif": return "image/gif";
                case ".svg": return "image/svg+xml";
                case ".ico": return "image/x-icon";
                default: return "application/octet-stream";
            }
        }
    }
}
