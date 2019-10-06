package sk.umb.prog3.hra2d.gui;

import javax.swing.JFrame;

/**
 * Inspirovane videom https://www.youtube.com/watch?v=9dzhgsVaiSo
 * 
 * @author mvagac
 *
 */
public class Klavesnica {

	public static void main(String[] args) {
		javax.swing.SwingUtilities.invokeLater(new Runnable(){
			public void run() {
				vytvorAZobrazHlavneOkno();
			}
		});
	}

	private static void vytvorAZobrazHlavneOkno() {
		JFrame window = new JFrame("Klavesnica");
		HlavneOkno okno = new HlavneOkno();
		window.setContentPane(okno);
		window.addWindowListener(okno);
//		window.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
		window.setResizable(false);
		window.pack();
		window.setVisible(true);
	}

}
