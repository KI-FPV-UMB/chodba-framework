importPackage(Packages.sk.umb.prog3.hra2d.aktivne_prvky);

Pohyb = {
		DOLAVA : 0,
		DOPRAVA : 1,
		HORE : 2,
		DOLE: 3
}

// hrac
bludisko.nastavHraca(2, 2, 0.05, 0.3, "hrac.png");

// prisera 1
bludisko.pridajAktivnyPrvok(1, 2, "prisera1.png", new SpravanieAktivnehoPrvku() {
	inicializuj: function(ap) {
		this.ap = ap;
		ap.nastavVlastnost('delta', 0.05);
		ap.nastavVlastnost('pohyb', 0);
		var r = Math.round(Math.random()*4);
		switch (r) {
		case 0:
			ap.nastavVlastnost('pohyb', Pohyb.DOPRAVA);
			break;
		case 1:
			ap.nastavVlastnost('pohyb', Pohyb.DOLAVA);
			break;
		case 2:
			ap.nastavVlastnost('pohyb', Pohyb.HORE);
			break;
		case 3:
			ap.nastavVlastnost('pohyb', Pohyb.DOLE);
			break;
		}
	},
	uprav: function() {
		var delta = parseFloat(this.ap.citajVlastnost('delta'));
		var pohyb = this.ap.citajVlastnost('pohyb');
		if (pohyb==Pohyb.DOPRAVA) {
			this.ap.zmenX(delta);
			if (this.ap.getX()>this.ap.getMaxX()) {
				pohyb = Pohyb.DOLAVA;
			}
		}
		if (pohyb==Pohyb.DOLAVA) {
			this.ap.zmenX(-delta);
			if (this.ap.getX()<0) {
				pohyb = Pohyb.DOPRAVA;
			}
		}
		if (pohyb==Pohyb.HORE) {
			this.ap.zmenY(delta);
			if (this.ap.getY()>this.ap.getMaxY()) {
				pohyb = Pohyb.DOLE;
			}
		}
		if (pohyb==Pohyb.DOLE) {
			this.ap.zmenY(-delta);
			if (this.ap.getY()<0) {
				pohyb = Pohyb.HORE;
			}
		}
		this.ap.nastavVlastnost('pohyb', pohyb);
	},
	kolizia: function(h) {
	}
});

// prisera 2
bludisko.pridajAktivnyPrvok(1, 1, "prisera2.png", new SpravanieAktivnehoPrvku() {
	inicializuj: function(ap) {
		this.ap = ap;
		ap.nastavVlastnost('delta', 0.05);
		ap.nastavVlastnost('pohyb', 0);
		var r = Math.round(Math.random()*4);
		switch (r) {
		case 0:
			ap.nastavVlastnost('pohyb', Pohyb.DOPRAVA);
			break;
		case 1:
			ap.nastavVlastnost('pohyb', Pohyb.DOLAVA);
			break;
		case 2:
			ap.nastavVlastnost('pohyb', Pohyb.HORE);
			break;
		case 3:
			ap.nastavVlastnost('pohyb', Pohyb.DOLE);
			break;
		}
	},
	uprav: function() {
		var delta = parseFloat(this.ap.citajVlastnost('delta'));
		var pohyb = this.ap.citajVlastnost('pohyb');
		if (pohyb==Pohyb.DOPRAVA) {
			this.ap.zmenX(delta);
			if (this.ap.getX()>this.ap.getMaxX()) {
				pohyb = Pohyb.DOLAVA;
			}
		}
		if (pohyb==Pohyb.DOLAVA) {
			this.ap.zmenX(-delta);
			if (this.ap.getX()<0) {
				pohyb = Pohyb.DOPRAVA;
			}
		}
		if (pohyb==Pohyb.HORE) {
			this.ap.zmenY(delta);
			if (this.ap.getY()>this.ap.getMaxY()) {
				pohyb = Pohyb.DOLE;
			}
		}
		if (pohyb==Pohyb.DOLE) {
			this.ap.zmenY(-delta);
			if (this.ap.getY()<0) {
				pohyb = Pohyb.HORE;
			}
		}
		this.ap.nastavVlastnost('pohyb', pohyb);
	},
	kolizia: function(h) {
	}
});

// bonus
bludisko.pridajAktivnyPrvok(3, 1, "bonus.png", new SpravanieAktivnehoPrvku() {
	inicializuj: function(ap) {
		this.ap = ap;
		ap.nastavVlastnost('stav', 0);
		ap.nastavVlastnost('pauza', 50);
		ap.nastavVlastnost('casZaciatok', Date.now());
	},
	uprav: function() {
		var stav = this.ap.citajVlastnost('stav');
		var elapsed = (Date.now() - parseInt(this.ap.citajVlastnost('casZaciatok')));
		if(elapsed > parseInt(this.ap.citajVlastnost('pauza'))) {
			stav++;
			this.ap.nastavVlastnost('casZaciatok', Date.now());
		}
		if (stav>40) {
			stav = 0;
		}
		this.ap.nastavVlastnost('stav', stav);
	},
	kolizia: function(h) {
	}
});
