package sk.umb.prog3.hra2d.gui;

import java.io.Serializable;

public class KlavesaSprava implements Serializable {

    private String klavesa;
    private String stav;

    public String getKlavesa() {
        return klavesa;
    }

    public void setKlavesa(String klavesa) {
        this.klavesa = klavesa;
    }

    public String getStav() {
        return stav;
    }

    public void setStav(String stav) {
        this.stav = stav;
    }

}
