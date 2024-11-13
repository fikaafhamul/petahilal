from skyfield import api
from skyfield import almanac
from skyfield.nutationlib import iau2000b
from datetime import timedelta
from pytz import timezone
from . import fungsi

ts = api.load.timescale()
e = api.load('de440s.bsp')  # Menggunakan ephemeris DE440s

class awalbulan:
    def __init__(self, bulan, tahun, lat, lon, TZ='Asia/Jakarta'):
        self.bulan = bulan
        self.tahun = tahun
        self.lat = lat  # Latitude pengamat
        self.lon = lon  # Longitude pengamat
        self.TZ = TZ
        self.JDE = self.hitung_jde()  # Menghitung JDE saat inisialisasi
        self.konjungsi = self.new_moon()  # Mengambil nilai konjungsi saat inisialisasi
        self.moonrise_moonset = self.rise_set_moon()
        self.sunset, self.moonset, self.moonage, self.tinggi_geo, self.elongasi_geo, self.tinggi_topo, self.elongasi_topo = self.calculate_hilal()  # Simpan hasil ke atribut

    def hitung_jde(self):
        # Menghitung Hy
        Hy = self.tahun + (((self.bulan - 1) * 29.53) / 354.3671)

        # Menghitung K
        K = round(((Hy - 1410) * 12), 0) - 129

        # Menghitung T
        T = K / 1236.85

        # Menghitung JDE
        JDE = 2451550.09765 + 29.530588853 * K + 0.0001337 * (T ** 2)

        return JDE

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
        konjungsi_time = self.konjungsi[0]

        # Menentukan rentang waktu untuk pencarian matahari terbenam
        t0 = ts.utc(konjungsi_time.year, konjungsi_time.month, konjungsi_time.day, 0, 0)
        t1 = t0 + timedelta(days=1)

        # Menghitung Lintang dan Bujur Pengamat
        longlat = api.Topos(latitude=self.lat, longitude=self.lon)

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

        # Menghitung Tinggi dan Elongasi Geosentris Bulan
        earth_pos = earth.at(sunset_time[0])
        moon_pos = earth_pos.observe(moon)
        sun_pos = earth_pos.observe(sun)
        geo_moon = moon_pos.apparent()
        geo_sun = sun_pos.apparent()
        alt_geo, az, distance = geo_moon.altaz()
        el_geo = geo_moon.separation(geo_sun)

        # Menghitung Tinggi dan Elongasi Toposentris Bulan
        observer = earth + longlat
        topo_moon = observer.at(sunset_time[0]).observe(moon).apparent()
        topo_sun = observer.at(sunset_time[0]).observe(sun).apparent()
        alt_topo, az, distance = topo_moon.altaz()
        el_topo = topo_moon.separation(topo_sun)
        
        return sunset_time_local, moonset_time_local, moonage, alt_geo, el_geo, alt_topo, el_topo
