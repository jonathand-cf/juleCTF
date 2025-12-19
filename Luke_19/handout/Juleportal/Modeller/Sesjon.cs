namespace Juleportal.Modeller
{
    public class Sesjon
    {
        public string SesjonsId { get; set; }
        public int BrukerId { get; set; }
        public string Epost { get; set; }
        public bool ErAdministrator { get; set; }
        public long OpprettetTidspunkt { get; set; }
        public long UtloperTidspunkt { get; set; }
    }
}
