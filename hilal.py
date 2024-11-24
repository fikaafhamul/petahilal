from skyfield import api
from skyfield import almanac
from skyfield.nutationlib import iau2000b
from datetime import timedelta
from pytz import timezone
from . import fungsi

ts = api.load.timescale()
e = api.load('de440s.bsp')  # Menggunakan ephemeris DE440s

class awalbulan:
    def __init__(self, bulan, tahun, lat, lon, TZ='Asia/Jakarta', TT = 0, TH = 0, kriteria = 'NEO MABIMS'):
        self.bulan = bulan
        self.tahun = tahun
        if self.bulan < 2:
            self.bulan1 = bulan - 1 + 12
            self.tahun1 = tahun - 1
        else:
            self.bulan1 = bulan - 1
            self.tahun1 = tahun
        self.lat = lat  # Latitude pengamat
        self.lon = lon  # Longitude pengamat
        self.TZ = TZ
        self.TT = TT
        self.TH = TH
        self.kriteria = kriteria
        self.JDE = self.hitung_jde()  # Menghitung JDE saat inisialisasi
        self.newmoon = self.new_moon()  # Mengambil nilai konjungsi saat inisialisasi
        self.moonrise_moonset = self.rise_set_moon()
        self.konjungsi, self.jd, self.sunset, self.moonset, self.altitude, self.elongasi, self.moonage = self.calculate_hilal()  # Simpan hasil ke atribut

    def hitung_jde(self):
        # Menghitung Hy
        Hy = self.tahun1 + (((self.bulan1 - 1) * 29.53) / 354.3671)

        # Menghitung K
        K = round(((Hy - 1410) * 12), 0) - 129

        # Menghitung T
        T = K / 1236.85

        # Menghitung JDE
        JDE = 2451550.09765 + 29.530588853 * K + 0.0001337 * (T ** 2)

        return JDE

    def cetak(self):
        

    def new_moon(self):
        temp = fungsi.caldat(self.JDE, 0, "JD_LENGKAP").result
        temp = list(temp)

        # Mengonversi JDE ke waktu UTC
        jd_time = ts.utc(temp[2], temp[1], temp[0], 0)

        # Mengatur rentang waktu untuk pencarian New Moon
        t0 = jd_time - timedelta(days=2)
        t1 = jd_time + timedelta(days=2)

        # Mencari fase bulan
        phases_time, y = almanac.find_discrete(t0, t1, almanac.moon_phases(e))

        # Mengambil waktu New Moon
        new_moon_times = phases_time[y == 0]  # 0 menandakan New Moon

        # Mengatur zona waktu (WIB)
        ZonaWaktu = timezone(self.TZ)
        return new_moon_times.astimezone(ZonaWaktu)

    def rise_set_moon(self):
        moon = e['moon']
        longlat = api.Topos(latitude=self.lat, longitude=self.lon)
        topos_at = (e['earth'] + longlat).at
        def is_moon_up_at(t):
            t._nutation_angles = iau2000b(t.tt)
            return topos_at(t).observe(moon).apparent().altaz()[0].degrees > -50/60
        is_moon_up_at.rough_period = 0.5
        return is_moon_up_at
        
    def calculate_hilal(self):
        # Ambil waktu konjungsi pertama
        konjungsi_time = self.newmoon[0]

        # Menentukan rentang waktu untuk pencarian matahari terbenam
        t0 = ts.utc(konjungsi_time.year, konjungsi_time.month, konjungsi_time.day, 0, 0)
        t1 = t0 + timedelta(days=1)

        # Menghitung Lintang dan Bujur Pengamat
        longlat = api.Topos(latitude=self.lat, longitude=self.lon, elevation_m=self.TT)

        # Menghitung waktu terbenam matahari
        sunriset, sunBol = almanac.find_discrete(t0, t1, almanac.sunrise_sunset(e, longlat))
        sunset_time = sunriset[sunBol == 0]  # 0 menandakan waktu terbenam

        # Ubah ke waktu UTC
        sunset_time_utc = sunset_time.utc_iso()

        # Ubah ke waktu lokal
        ZonaWaktu = timezone(self.TZ)
        sunset_time_local = sunset_time.astimezone(ZonaWaktu)

        # Menghitung Umur Bulan
        temp = konjungsi_time.hour + (konjungsi_time.minute)/60 + (konjungsi_time.second)/3600
        temp1 = sunset_time_local[0]
        temp1 = temp1.hour + (temp1.minute)/60 + (temp1.second)/3600
        moonage = (temp1 - temp)

        # Menghitung waktu terbenam Bulan
        moonriset, moonBol = almanac.find_discrete(t0, t1, self.moonrise_moonset)
        moonset_time = moonriset[moonBol == 0]

        # Ubah ke waktu UTC
        moonset_time_utc = moonset_time.utc_iso()

        # Ubah ke waktu lokal
        moonset_time_local = moonset_time.astimezone(ZonaWaktu)

        # import data benda langit
        earth = e['earth']
        moon = e['moon']
        sun = e['sun']
        observer = earth + longlat

        # Menghitung Tinggi dan Elongasi Bulan
        geo_moon = earth.at(sunset_time[0]).observe(moon).apparent()
        geo_sun = earth.at(sunset_time[0]).observe(sun).apparent()
        el_geo = geo_sun.separation_from(geo_moon).degrees

        topo_moon = observer.at(sunset_time[0]).observe(moon).apparent()
        topo_sun = observer.at(sunset_time[0]).observe(sun).apparent()
        alt, az, distance = topo_moon.altaz()
        alt = alt.degrees
        el_topo = topo_sun.separation_from(topo_moon).degrees

        kriteria = self.kriteria.upper()
        if kriteria == "IRNU":
            jd = (t0 + timedelta(days=1)) if (alt >= 3 and el_geo >= 6.4) or (el_geo > 9.9) else (t0 + timedelta(days=2))
        elif kriteria == "MUHAMADIYYAH":
            jd = (t0 + timedelta(days=1)) if (alt >= 0) else (t0 + timedelta(days=2))
        elif kriteria == "MABIMS LAMA":
            jd = (t0 + timedelta(days=1)) if (alt >= 2 and el_geo >= 3 and moonage >= 8) else (t0 + timedelta(days=2))
        elif kriteria == "NEO MABIMS":
            jd = (t0 + timedelta(days=1)) if (alt >= 3 and el_geo >= 6.4) else (t0 + timedelta(days=2))

        jd = jd + timedelta(days=28) + self.TH

        # Mengatur rentang waktu untuk pencarian New Moon
        t0 = jd - timedelta(days=2)
        t1 = jd + timedelta(days=2)

        # Mencari fase bulan
        phases_time, y = almanac.find_discrete(t0, t1, almanac.moon_phases(e))

        # Mengambil waktu New Moon
        new_moon_times = phases_time[y == 0]  # 0 menandakan New Moon
        new_moon_times = new_moon_times.astimezone(ZonaWaktu)

        konjungsi_times = new_moon_times[0]

        sunriset, sunBol = almanac.find_discrete(t0, t1, almanac.sunrise_sunset(e, longlat))
        sunset_time = sunriset[sunBol == 0]  # 0 menandakan waktu terbenam

        # Ubah ke waktu UTC
        sunset_time_utc = sunset_time.utc_iso()

        # Ubah ke waktu lokal
        sunset_time_local = sunset_time.astimezone(ZonaWaktu)

        # Menghitung Umur Bulan
        temp = konjungsi_time.hour + (konjungsi_time.minute)/60 + (konjungsi_time.second)/3600
        temp1 = sunset_time_local[0]
        temp1 = temp1.hour + (temp1.minute)/60 + (temp1.second)/3600
        moonage = (temp1 - temp)

        # Menghitung waktu terbenam Bulan
        moonriset, moonBol = almanac.find_discrete(t0, t1, self.moonrise_moonset)
        moonset_time = moonriset[moonBol == 0]

        # Ubah ke waktu UTC
        moonset_time_utc = moonset_time.utc_iso()

        # Ubah ke waktu lokal
        moonset_time_local = moonset_time.astimezone(ZonaWaktu)

        # Menghitung Tinggi dan Elongasi Bulan
        geo_moon = earth.at(sunset_time[0]).observe(moon).apparent()
        geo_sun = earth.at(sunset_time[0]).observe(sun).apparent()
        el_geo = geo_sun.separation_from(geo_moon).degrees

        topo_moon = observer.at(sunset_time[0]).observe(moon).apparent()
        topo_sun = observer.at(sunset_time[0]).observe(sun).apparent()
        alt, az, distance = topo_moon.altaz()
        alt = alt.degrees
        el_topo = topo_sun.separation_from(topo_moon).degrees

        return konjungsi_times, jd, sunset_time_local, moonset_time_local, alt, el_topo, moonage
