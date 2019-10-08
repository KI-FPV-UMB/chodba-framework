package sk.umb.prog3.hra2d.bludisko;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertNotNull;

import java.io.IOException;

import javax.script.ScriptException;

import org.junit.Test;

/**
 * 
 * @author mvagac
 *
 */
public class BludiskoTest {

	@Test
	public void testFunkcionalityABC() throws IOException, ScriptException {
		Bludisko bludisko = new Bludisko(null, "utest/");
		bludisko.uprav();
		// bludisko
		assertEquals(7, bludisko.getSirka());
		assertEquals(5, bludisko.getVyska());
		// dlazdice
/*		assertEquals(3, bludisko.getDlazdice().size());
		assertEquals(true, bludisko.getDlazdice().get(0).priechodna);
		assertEquals(false, bludisko.getDlazdice().get(1).priechodna);
		assertEquals(false, bludisko.getDlazdice().get(2).priechodna);
		// aktivne prvky
		assertNotNull(bludisko.getHrac());
		assertEquals(3, bludisko.getAktivnePrvky().size());
		// aktivne prvky - prisera 1
		assertEquals(true, bludisko.getAktivnePrvky().get(0) instanceof Prisera);
		Prisera p1 = (Prisera)bludisko.getAktivnePrvky().get(0);
		assertEquals(1f, p1.getX(), 0.0001);
		assertEquals(2f, p1.getY(), 0.0001);
		// aktivne prvky - prisera 2
		assertEquals(true, bludisko.getAktivnePrvky().get(1) instanceof Prisera);
		Prisera p2 = (Prisera)bludisko.getAktivnePrvky().get(1);
		assertEquals(1f, p2.getX(), 0.0001);
		assertEquals(1f, p2.getY(), 0.0001);
		// aktivne prvky - bonus
		assertEquals(true, bludisko.getAktivnePrvky().get(2) instanceof Bonus);
		Bonus b = (Bonus)bludisko.getAktivnePrvky().get(2);
		assertEquals(3f, b.getX(), 0.0001);
		assertEquals(2f, b.getY(), 0.0001);
*/
	}

}
