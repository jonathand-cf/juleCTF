namespace Juleportal.Modeller
{
    public class Bruker
    {
        public int Id { get; set; }
        public string Epost { get; set; }
        public string PassordHash { get; set; }
        public bool ErAdministrator { get; set; }
        public string Tilbakestillingskode { get; set; }
        public long? TilbakestillingskodeUtloper { get; set; }
    }
}
