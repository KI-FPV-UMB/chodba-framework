package sk.umb.prog3.hra2d.bludisko;

import java.awt.image.BufferedImage;
import java.io.IOException;

import javax.imageio.ImageIO;

/**
 * 
 * @author mvagac
 *
 */
public class DlazdicaGrafika extends Dlazdica {

	private BufferedImage obrazok;

	public DlazdicaGrafika(boolean priechodna, String nazovSuboru) throws IOException {
		super(priechodna);
		obrazok = ImageIO.read(getClass().getResourceAsStream(nazovSuboru));
	}

	public BufferedImage getObrazok() {
		return obrazok;
	}

}
