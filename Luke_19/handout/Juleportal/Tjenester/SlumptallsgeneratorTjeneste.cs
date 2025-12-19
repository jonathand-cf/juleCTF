using System;
using System.Diagnostics;

namespace Juleportal.Tjenester
{
    public class SlumptallsgeneratorTjeneste
    {
        public string GenererForespørselsId()
        {
            var slumptallsgenerator = new Random();
            
            var bytes = new byte[16];
            slumptallsgenerator.NextBytes(bytes);
            
            return new Guid(bytes).ToString();
        }

        public string GenererTilbakestillingskode()
        {
            var slumptallsgenerator = new Random();

            var kodeBytes = new byte[10];
            slumptallsgenerator.NextBytes(kodeBytes);

            return Convert.ToBase64String(kodeBytes);
        }
    }
}
