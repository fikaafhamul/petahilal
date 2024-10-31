class konversi:
    def __init__(self, angle, pilihan="DERAJAT"):
        self.angle = angle  # Menyimpan nilai angle ke dalam atribut instance
        pilihan = pilihan.upper()
        if pilihan == "DERAJAT":
            self.result = self.deg2dms()
        elif pilihan == "JAM":
            self.result = self.deg2hms()
        elif pilihan == "DERAJAT1":
            self.result = self.deg2dms1()
        elif pilihan == "JAM1":
            self.result = self.deg2hms1()
        else:
            self.result = self.deg2dms()

    def deg2dms(self):
        D = int(abs(self.angle))
        M = int((abs(self.angle) - D) * 60)
        S = (abs(self.angle) - D - M / 60) * 3600

        # Check for rounding issues
        if S >= 60:
            S = 0
            M += 1
        if M >= 60:
            M = 0
            D += 1

        if self.angle < 0:
            return f"-{D}° {M:02}' {S:05.2f}\""
        else:
            return f"{D}° {M:02}' {S:05.2f}\""

    def deg2hms(self):
        D = int(abs(self.angle))
        M = int((abs(self.angle) - D) * 60)
        S = (abs(self.angle) - D - M / 60) * 3600

        # Check for rounding issues
        if S >= 60:
            S = 0
            M += 1
        if M >= 60:
            M = 0
            D += 1

        if self.angle < 0:
            return f"-{D:02} : {M:02} : {S:05.2f}"
        else:
            return f"{D:02} : {M:02} : {S:05.2f}"

    def deg2dms1(self):
        D = int(abs(self.angle))
        M = int((abs(self.angle) - D) * 60)
        S = (abs(self.angle) - D - M / 60) * 3600

        # Check for rounding issues
        if S >= 60:
            S = 0
            M += 1
        if M >= 60:
            M = 0
            D += 1

        if self.angle < 0:
            if D == 0 and M == 0:
                return f"-{S:05.2f}\""
            elif D == 0:
                return f"-{M:02}' {S:05.2f}\""
            else:
                return f"-{D}° {M:02}' {S:05.2f}\""
        else:
            if D == 0 and M == 0:
                return f"{S:05.2f}\""
            elif D == 0:
                return f"{M:02}' {S:05.2f}\""
            else:
                return f"{D}° {M:02}' {S:05.2f}\""

    def deg2hms1(self):
        D = int(abs(self.angle))
        M = int((abs(self.angle) - D) * 60)
        S = (abs(self.angle) - D - M / 60) * 3600

        # Check for rounding issues
        if S >= 60:
            S = 0
            M += 1
        if M >= 60:
            M = 0
            D += 1

        if self.angle < 0:
            if D == 0 and M == 0:
                return f"-{S:05.2f} detik"
            elif D == 0:
                return f"-{M:02} Menit {S:05.2f} Detik"
            else:
                return f"-{D } jam {M:02} Menit {S:05.2f} Detik"
        else:
            if D == 0 and M == 0:
                return f"{S:05.2f} detik"
            elif D == 0:
                return f"{M:02} Menit {S:05.2f} Detik"
            else:
                return f"{D} jam {M:02} Menit {S:05.2f} Detik"

#print(konversi(287.856956).result)

class hijriah:
    def __init__(self):
        self.bulan_hijriah = lambda bulan: self.b2_hijri(bulan) if isinstance(bulan, int) else self.hijri_to_b(bulan)

    def b2_hijri(self, bulan: int) -> str:
        if bulan == 1:
            return "Muharram"
        elif bulan == 2:
            return "Shafar"
        elif bulan == 3:
            return "Rabi'ul Awal"
        elif bulan == 4:
            return "Rabi'ul Akhir"
        elif bulan == 5:
            return "Jumadil Awal"
        elif bulan == 6:
            return "Jumadil Akhir"
        elif bulan == 7:
            return "Rajab"
        elif bulan == 8:
            return "Sya'ban"
        elif bulan == 9:
            return "Ramadlan"
        elif bulan == 10:
            return "Syawal"
        elif bulan == 11:
            return "Dzul Qo'dah"
        elif bulan == 12:
            return "Dzul Hijjah"
        else:
            return ""

    def hijri_to_b(self, bulan: str) -> int:
        if bulan == "Muharram":
            return 1
        elif bulan == "Shafar":
            return 2
        elif bulan == "Rabi'ul Awal":
            return 3
        elif bulan == "Rabi'ul Akhir":
            return 4
        elif bulan == "Jumadil Awal":
            return 5
        elif bulan == "Jumadil Akhir":
            return 6
        elif bulan == "Rajab":
            return 7
        elif bulan == "Sya'ban":
            return 8
        elif bulan == "Ramadlan":
            return 9
        elif bulan == "Syawal":
            return 10
        elif bulan == "Dzul Qo'dah":
            return 11
        elif bulan == "Dzul Hijjah":
            return 12
        else:
            return 0


class miladi:
    def __init__(self):
        self.bulan_miladi = lambda bulan: self.b2_miladi(bulan) if isinstance(bulan, int) else self.miladi_to_b(bulan)

    def b2_miladi(self, bulan: int) -> str:
        if bulan == 1:
            return "Januari"
        elif bulan == 2:
            return "Februari"
        elif bulan == 3:
            return "Maret"
        elif bulan == 4:
            return "April"
        elif bulan == 5:
            return "Mei"
        elif bulan == 6:
            return "Juni"
        elif bulan == 7:
            return "Juli"
        elif bulan == 8:
            return "Agustus"
        elif bulan == 9:
            return "September"
        elif bulan == 10:
            return "Oktober"
        elif bulan == 11:
            return "November"
        elif bulan == 12:
            return "Desember"
        else:
            return ""

    def miladi_to_b(self, bulan: str) -> int:
        if bulan == "Januari":
            return 1
        elif bulan == "Februari":
            return 2
        elif bulan == "Maret":
            return 3
        elif bulan == "April":
            return 4
        elif bulan == "Mei":
            return 5
        elif bulan == "Juni":
            return 6
        elif bulan == "Juli":
            return 7
        elif bulan == "Agustus":
            return 8
        elif bulan == "September":
            return 9
        elif bulan == "Oktober":
            return 10
        elif bulan == "November":
            return 11
        elif bulan == "Desember":
            return 12
        else:
            return 0

# Contoh penggunaan
#print(hijriah().bulan_hijriah(1))  # Output: Muharram
#print(hijriah().bulan_hijriah("Muharram"))  # Output: 1

#print(miladi().bulan_miladi(1))  # Output: Januari
#print(miladi().bulan_miladi("Januari"))  # Output
