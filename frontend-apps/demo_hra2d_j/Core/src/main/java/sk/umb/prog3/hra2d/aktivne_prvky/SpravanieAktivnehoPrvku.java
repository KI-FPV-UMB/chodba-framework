package sk.umb.prog3.hra2d.aktivne_prvky;

/**
 * 
 * @author mvagac
 *
 */
public interface SpravanieAktivnehoPrvku {

	public void inicializuj(AktivnyPrvok ap);

	public void uprav();

	public void kolizia(Hrac h);

}
