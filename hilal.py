class awalbulan:
    def __init__(self, bulan, tahun, TZ='Asia/Jakarta'):
        self.bulan = bulan
        self.tahun = tahun
        self.TZ = TZ
        self.JDE = self.hitung_jde()  # Menghitung JDE saat inisialisasi
        self.konjungsi = self.new_moon()  # Mengambil nilai konjungsi saat inisialisasi
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



#tahun = 1446
#bulan = 5
#awal_bulan = awalbulan(bulan, tahun)

#print(f"Nilai JDE untuk Tahun {awal_bulan.tahun} dan Bulan {awal_bulan.bulan} adalah: {awal_bulan.JDE}")
#a = awal_bulan.konjungsi[0]
#print(a.year)
#print(f"Waktu Konjungsi Bulan adalah: {a.strftime('%Y-%m-%d %H:%M:%S.%f %Z')}")
