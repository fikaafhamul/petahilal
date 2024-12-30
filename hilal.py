from skyfield import api
from skyfield import almanac
from skyfield.nutationlib import iau2000b
from skyfield.framelib import ecliptic_frame
from datetime import timedelta
from pytz import timezone
from math import sin, cos, asin, degrees, radians
from . import fungsi
import requests
from bs4 import BeautifulSoup

ts = api.load.timescale()
e = api.load('de440s.bsp')  # Menggunakan ephemeris DE440s

_all_ = ["visibilitas_oddeh", "awalbulan"]
	
def visibilitas_oddeh(sunset, lag, separasi, lebar_sabit):
    # Menghitung Best Time
    best_time = sunset + 4/9 * lag
		    
    # Menghitung q
    lebar_sabit = lebar_sabit	    
    q = separasi - (-0.1018 * (lebar_sabit ** 3) + 0.7319 * (lebar_sabit ** 2) - 6.3226 * lebar_sabit + 7.1651)

    # Parameter
    if q >= 5.65:
        parameter = "Mudah teramati tanpa alat bantu optik"
    elif (q < 5.65 and q >= 2):
        parameter = "Mungkin teramati tanpa alat bantu optik"
    elif (q < 2 and q >= -0.96):
        parameter = "Terlihat hanya dengan alat bantu optik"
    elif (q < -0.96):
        parameter = "Tidak terlihat"

    return best_time, q, parameter

class awalbulan:
    def __init__(self, bulan, tahun, lok, lat, lon, TZ='Asia/Jakarta', TT = 0, TH = 0, kriteria = 'NEO MABIMS', id_cuaca = ' ', jam_cuaca = '16.00 WIB'):
        self.bulan = bulan
        self.tahun = tahun
        if self.bulan < 2:
            self.bulan1 = bulan - 1 + 12
            self.tahun1 = tahun - 1
        else:
            self.bulan1 = bulan - 1
            self.tahun1 = tahun
        self.lokasi = lok  # Nama Lokasi
        self.lat = lat  # Latitude pengamat
        self.lon = lon  # Longitude pengamat
        self.TZ = TZ
        self.TT = TT
        self.TH = TH
        self.kriteria = kriteria
        self.id_cuaca = id_cuaca
        self.jam_cuaca = jam_cuaca
        self.JDE = self.hitung_jde()  # Menghitung JDE saat inisialisasi
        self.newmoon = self.new_moon()  # Mengambil nilai konjungsi saat inisialisasi
        self.moonrise_moonset = self.rise_set_moon()
        self.konjungsi, self.jd, self.sunset, self.moonset, self.altitude, self.elongasi, self.moonage= self.calculate_hilal()  # Simpan hasil ke atribut
        self.jam, self.suhu, self.kelembapan, self.kecepatan, self.arahangin, self.jarakpandang, self.situasi = self.weather()
        self.cetak = self.cetak()
	    
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

        sunriset, sunBol = almanac.find_discrete(jd, jd + timedelta(days=1), almanac.sunrise_sunset(e, longlat))
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
        moonriset, moonBol = almanac.find_discrete(jd, jd + timedelta(days=1), self.moonrise_moonset)
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

    def weather(self):
        url = f"https://www.bmkg.go.id/cuaca/prakiraan-cuaca/{self.id_cuaca}"

        # Mengirim permintaan HTTP
        response = requests.get(url)

        # Memeriksa apakah permintaan berhasil
        if response.status_code == 200:
            # Mem-parsing konten HTML
            soup = BeautifulSoup(response.content, 'html.parser')

            # Mencari elemen yang berisi data cuaca
            c = soup.find_all('p', class_='text-[32px] leading-[48px] md:text-[48px] md:leading-[62px] font-bold')         
            suhu = []
            for data in c:
                suhu.append(data.text)

            j = soup.find_all('h4', class_='text-base leading-[25px] md:text-2xl font-bold') 
            jam = []
            for data in j:
                jam.append(data.text)
    
            k = soup.find_all('p', class_='text-black-primary font-bold text-xs md:text-base md:leading-[25px] gap-2')
            kondisi = []
            for data in k:
                kondisi.append(data.text)

            ar = soup.find_all('span', class_='text-black-primary font-bold')
            arah = []
            for data in ar:
                arah.append(data.text)

            kn = soup.find_all('p', class_='text-sm md:text-lg font-bold mt-4')
            situasi = []
            for data in kn:
                situasi.append(data.text)
        else:
            print("Gagal mengambil data cuaca")

        j = jam.index(self.jam_cuaca)
        if j == 0:
            kelembapan = kondisi[j]
            kec = kondisi[j+1]
            jarak = kondisi[j+2]
        else:
            kelembapan = kondisi[j*3]
            kec = kondisi[j*3+1]
            jarak = kondisi[j*3+2]
		
        return jam[j], suhu[j], kelembapan, kec, arah[j+4], jarak, situasi[j]

    def cetak(self):
        bln_h = fungsi.hijriah().bulan_hijriah(self.bulan)
        thn_h = self.tahun
        latitude = fungsi.konversi(self.lat, "LINTANG").result
        longitude = fungsi.konversi(self.lon, "BUJUR").result
        konjungsi = self.konjungsi
        n1_bln = fungsi.miladi().bulan_miladi(konjungsi.month)
        ZonaWaktu = timezone(self.TZ)

        # Menghitung Lintang dan Bujur Pengamat
        longlat = api.Topos(latitude=self.lat, longitude=self.lon, elevation_m=self.TT)

        # import data benda langit
        earth = e['earth']
        moon = e['moon']
        sun = e['sun']
        observer = earth + longlat

        # Mengatur rentang waktu
        t0 = self.jd
        t1 = t0 + timedelta(days=1)

        sunriset, sunBol = almanac.find_discrete(t0, t1, almanac.sunrise_sunset(e, longlat))
        sunset_time = sunriset[sunBol == 0]  # 0 menandakan waktu terbenam

        # Ubah ke waktu UTC
        sunset_time_utc = sunset_time.utc_iso()

        # Ubah ke waktu lokal
        sunset_time_local = sunset_time.astimezone(ZonaWaktu)

        # Menghitung waktu terbenam Bulan
        moonriset, moonBol = almanac.find_discrete(t0, t1, self.moonrise_moonset)
        moonset_time = moonriset[moonBol == 0]

        # Ubah ke waktu UTC
        moonset_time_utc = moonset_time.utc_iso()

        # Ubah ke waktu lokal
        moonset_time_local = moonset_time.astimezone(ZonaWaktu)

        # Menghitung Tinggi, azimut dan Elongasi Bulan
        geo_moon = earth.at(sunset_time[0]).observe(moon).apparent()
        geo_sun = earth.at(sunset_time[0]).observe(sun).apparent()
        el_geo = geo_sun.separation_from(geo_moon).degrees

        topo_moon = observer.at(sunset_time[0]).observe(moon).apparent()
        topo_sun = observer.at(sunset_time[0]).observe(sun).apparent()
        moon_alt, moon_az, moon_distance = topo_moon.altaz()
        moon_alt, moon_az = moon_alt.degrees, moon_az.degrees
        sun_alt, sun_az, sun_distance = topo_sun.altaz()
        sun_alt, sun_az = sun_alt.degrees, sun_az.degrees
        el_topo = topo_sun.separation_from(topo_moon).degrees

	# Menghitung Iluminasi Bulan
        illumination = topo_moon.fraction_illuminated(sun)*100 

	# Menghitung Lebar Sabit Bulan
        horizontalparalax = degrees(asin(6378.14/moon_distance.km))
        semidiameter= (358473400/moon_distance.km)/3600
        SD = semidiameter * horizontalparalax
        SD1 = SD * (1 + sin(radians(moon_alt))*sin(radians(horizontalparalax)))
        W = SD1 * (1-cos(radians(el_topo)))
	
        # Menghitung Umur Bulan
        temp = konjungsi.hour + (konjungsi.minute)/60 + (konjungsi.second)/3600
        temp1 = sunset_time_local[0]
        temp1 = temp1.hour + (temp1.minute)/60 + (temp1.second)/3600
        moonage = (temp1 - temp)

        sunset = sunset_time_local[0]
        moonset = moonset_time_local[0]
	    
	# Lama Hilal
        temp = sunset.hour + (sunset.minute)/60 + (sunset.second)/3600
        temp1 = moonset.hour + (moonset.minute)/60 + (moonset.second)/3600
        lag_time = (temp1 - temp)

        separasi = moon_alt - sun_alt
        best_time, q, parameter = visibilitas_oddeh(temp, lag_time, separasi, W)
	    
        n_bln = fungsi.miladi().bulan_miladi(sunset.month)
        temp = sunset.tzinfo.utcoffset(sunset)
        delta_time_tz = int(temp.total_seconds()/3600)

        title = "Data Astronomi " + str(bln_h) + " " + str(thn_h) + " H"
        title1 = "Jet Propulsion Laboratory (JPL) Ephemeris, by Planetarium KH. Zubair Umar Al-Jailani"
	    
        print ('\n')
        print (f'{title:^120}')
        print (f'{title1:^120}')
        print ('\n')
        print ('- Perhitungan telah dilakukan untuk menentukan waktu matahari terbenam pada %02d:%02d:%02d di tanggal %d %s %d M' % (sunset.hour,sunset.minute,sunset.second,sunset.day,n_bln,sunset.year))
        print ('- Semua data disajikan dalam waktu lokal pengamat')
        if self.lokasi is None:
        	print ('Lokasi: ')
        else:
        	print ('- Lokasi: ' + self.lokasi)
        print ('   - Lintang: ' + latitude + '  Bujur: ' + longitude + '  Elevasi: %.2f m' % self.TT)
        if delta_time_tz<0:
        	print ('   - Time zone: ' + self.TZ + ' '+ str(delta_time_tz))
        else:
        	print ('   - Time zone: ' + self.TZ + ' +'+ str(delta_time_tz))
		
        print ('- Visibilitas Oddeh ')
        print ('   - Best Time: %s' % (fungsi.konversi(best_time,"JAM").result))
        print ('   - q: ' + str(round(q,2)))
        print ('   - Parameter: ' + parameter)
	    
        if self.id_cuaca == " ":
        	print ('')
        else:
        	print ('- Prakiraan cuaca pada jam ' + self.jam)
        print ('   - Suhu: ' + self.suhu)
        print ('   - Kondisi Langit: ' + self.situasi)
        print ('   - Kelembapan: ' + self.kelembapan)
        print ('   - Kecepatan Angin: ' + self.kecepatan)
        print ('   - Arah Angin: ' + self.arahangin)
        print ('   - Jarak Pandang: ' + self.jarakpandang)
        print (f'{"".join(["="]*120)} \n')
        print ('- Waktu Konjungsi         : %d %s %d M %02d:%02d:%02d LT' % (konjungsi.day,n1_bln,konjungsi.year,konjungsi.hour,konjungsi.minute,konjungsi.second))
        print ('- Waktu Matahari Terbenam : %02d:%02d:%02d                          - Waktu Bulan Terbenam             : %02d:%02d:%02d' % (sunset.hour,sunset.minute,sunset.second, moonset.hour,moonset.minute,moonset.second))
        print ('- Ketinggian Matahari     : %s                    - Ketinggian Bulan                 : %s' % (fungsi.konversi(sun_alt).result,fungsi.konversi(moon_alt).result))  
        print ('- Azimut Matahari         : %s                   - Azimut Bulan                     : %s' % (fungsi.konversi(sun_az).result,fungsi.konversi(moon_az).result))  
        print ('- Lebar Sabit Bulan       : %s                     - Elongasi Bulan (Geosentris)      : %s' % (fungsi.konversi(W).result,fungsi.konversi(el_geo).result))  
        print ('- Iluminasi Bulan         : %.2f %%                            - Elongasi Bulan (Toposentris)     : %s' % (float(illumination),fungsi.konversi(el_topo).result))  
        print ('- Umur Bulan              : %s        - Lama Bulan di atas Ufuk          : %s' % (fungsi.konversi(moonage, "JAM1").result,fungsi.konversi(lag_time,"JAM1").result))
