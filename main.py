import platform
import os
import math
import turtle
import random

raport_arr = []
zdarzenia = []

txt_eff = {"RESET": "\033[0m",
           "RED": "\033[1;31m",
           "GREEN": "\033[1;32m",
           "YELLOW": "\033[1;33m",
           "BLUE": "\033[1;34m",
           "PURPLE": "\033[1;35m",
           "CYAN": "\033[1;36m",
           "WHITE": "\033[1;37m",
           "ITALIC": "\033[3m",
           "BOLD": "\033[1m"}


def clamp(wartosc, min_war, max_war):
    if wartosc < min_war:
        return min_war
    elif wartosc > max_war:
        return max_war
    return wartosc

def get_distance(pos_a, pos_b):
    return math.sqrt((pos_a[0] - pos_b[0])**2 + (pos_a[1] - pos_b[1])**2)

def get_closest_object(cent, objekt_list, rozmiar):
        closest = rozmiar + 1
        dist = [0.0,0,0,0,"rodzaj"]
        for obj in objekt_list:
            dist[0] = get_distance(cent.get_pos(), obj.get_pos())
            if dist[0] < 10:
                if type(obj) == GRACZ:
                    obj.usun(cent)
                elif obj.rodzaj == "przeciwnik":
                    obj.usun(cent)
                    continue
                else:
                    obj.usun(cent)
                    objekt_list.remove(obj)
                    continue
            if dist[0] < closest:
                closest = dist[0]
                dist[1] = obj.get_pos()[0]
                dist[2] = obj.get_pos()[1]
                dist[3] = obj.idx
                dist[4] = obj.rodzaj
        dist[0] = closest
        return dist

def ob_angle(cent, objekt_list, rozmiar):
    closest_obj = get_closest_object(cent, objekt_list, rozmiar)
    start_x = cent.get_pos()[0]
    start_y = cent.get_pos()[1]
    end_x = closest_obj[1]
    end_y = closest_obj[2]
    magnitude = closest_obj[0]/10
    return [[(end_x-start_x) / clamp(magnitude, 0.01, 500),(end_y-start_y) / clamp(magnitude, 0.01, 500)], closest_obj[0], closest_obj[4]]

def pl_angle(cent):
    pos_x = cent.get_pos()[0] + math.cos(math.radians(cent.get_rot())) * 10
    pos_y = cent.get_pos()[1] + math.sin(math.radians(cent.get_rot())) * 10
    return [pos_x - cent.get_pos()[0], pos_y - cent.get_pos()[1]]

def get_angle_and_distance(cent, objekt_list, rozmiar):
    obj = ob_angle(cent, objekt_list, rozmiar)
    vec_pl = pl_angle(cent)
    vec_ob = obj[0]
    ob_dist = obj[1]
    dot = vec_pl[0]*vec_ob[0] + vec_pl[1]*vec_ob[1]
    det = vec_pl[0]*vec_ob[1] - vec_pl[1]*vec_ob[0]
    angle = -math.degrees(math.atan2(det, dot))
    match obj[2]:
        case "przeciwnik":
            msg = f"{txt_eff['RED']}CEL SIE RUSZA!!!{txt_eff['RESET']} (wykrywa przeciwnika)"
        case "gracz":
            msg = ""
        case "zaopatrzenie":
            msg = f"{txt_eff['CYAN']}CEL NIERUCHOMY{txt_eff['RESET']} (wykrywa zaopatrzenie)"
        case _:
            msg = "nie wiem jakim cudem"

    return [angle, ob_dist, msg]


class GRACZ:
    def __init__(self, imie, pos_x, pos_y, kat, polaczenie, ilosc_zaopatrzenia):
        self.t = turtle.Turtle()
        self.t.speed(0)
        self.imie = imie
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.old_x = pos_x
        self.old_y = pos_y
        self.old_pol = polaczenie
        self.kat = kat
        self.t.setheading(kat)
        self.t.penup()
        self.t.setpos(pos_x, pos_y)
        self.t.pendown()
        self.polaczenie = polaczenie
        self.ilosc_zaopatrzenia = ilosc_zaopatrzenia
        self.idx = 0
        self.rodzaj = "gracz"

    def wypisz_wartosci(self):
        print(f"{txt_eff['GREEN']}Postać: {txt_eff['BLUE']}{self.imie}    "
              f"{txt_eff['GREEN']}x: {txt_eff['CYAN']}{round(self.pos_x, 2)} "
              f"{txt_eff['GREEN']}y: {txt_eff['CYAN']}{round(self.pos_y, 2)}   "
              f"{txt_eff['GREEN']}alfa: {txt_eff['CYAN']}{-self.kat}   "
              f"{txt_eff['RED']}połączenie: {self.polaczenie}{txt_eff['RESET']} (połączenie zmniejsza sie o 1 co ruch)\n\n"
              f"{txt_eff['GREEN']}POPRZEDNIE WARTOSCI:\nx: {self.old_x} y: {self.old_y}   połączenie: {self.old_pol}\n")

    def obrot(self, nowy_kat):
        self.kat -= nowy_kat
        if self.kat < -180: self.kat += 360
        elif self.kat > 180: self.kat -= 360
        self.t.setheading(self.t.heading() - nowy_kat)

    def ruch(self, distance):
        self.old_x = self.pos_x
        self.old_y = self.pos_y
        self.pos_x += round(math.cos(math.radians(self.kat)) * distance, 2)
        self.pos_y += round(math.sin(math.radians(self.kat)) * distance, 2)
        self.t.pendown()
        self.t.speed(1)
        self.t.goto(self.pos_x, self.pos_y)

    def get_pos(self):
        return [self.pos_x, self.pos_y]

    def set_pos(self, new_pos):
        self.pos_x = new_pos[0]
        self.pos_y = new_pos[1]
        self.t.speed(0)
        self.t.goto(new_pos)
        self.t.speed(1)

    def get_rot(self):
        return self.kat

    def usun(self, cent):
        pass

    def zmniejsz_zaopatrzenie(self):
        self.ilosc_zaopatrzenia -= 1
        if self.ilosc_zaopatrzenia == 0:
            stop()
            print("ZEBRANE WSZYSTKO")
            wyczysc_ekran()
            self.wypisz_wartosci()

class SWIAT:
    def __init__(self, rozmiar, poziom_trudnosci, ilosc_zaopatrzenia):
        self.rozmiar = rozmiar
        self.t = turtle.Turtle()
        self.rysuj_border()
        self.objekty = []
        self.ilosc_zaopatrzenia = ilosc_zaopatrzenia

        for i in range(self.ilosc_zaopatrzenia):
            self.stworz_objekt("zaopatrzenie")

        for i in range(poziom_trudnosci):
            self.stworz_objekt("przeciwnik")




    def rysuj_border(self):
        self.t.penup()
        self.t.speed(0)
        self.t.pensize(3)
        self.t.setpos(-self.rozmiar/2, -self.rozmiar/2)
        self.t.pendown()
        for i in range(0,4):
            self.t.forward(self.rozmiar)
            self.t.left(90)
        self.t.penup()
        self.t.hideturtle()
        del self.t

    def stworz_objekt(self, rodzaj):
        pos_x = random.randint(-self.rozmiar // 2, self.rozmiar // 2)
        pos_y = random.randint(-self.rozmiar // 2, self.rozmiar // 2)
        if len(self.objekty) == 0:
            self.objekty.append(OBJEKT(rodzaj, pos_x, pos_y, 0))
        else:
            while True:
                pos_x = random.randint(-self.rozmiar // 2, self.rozmiar // 2)
                pos_y = random.randint(-self.rozmiar // 2, self.rozmiar // 2)
                f = True
                for obj in self.objekty:
                    if get_distance((pos_x, pos_y), obj.get_pos()) < 100:
                        f = False
                if f:
                    self.objekty.append(OBJEKT(rodzaj, pos_x, pos_y, len(self.objekty)))
                    break

class OBJEKT:
    def __init__(self, rodzaj, pos_x, pos_y, idx):
        self.t = turtle.Turtle()

        self.t.hideturtle()
        self.rodzaj = rodzaj
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.idx = idx
        self.rysuj()
        self.kat = 0.0
        if rodzaj == "przeciwnik":
            self.kat = random.randint(-180, 180)
            self.t.setheading(self.kat)

    def rysuj(self):
        self.t.penup()
        self.t.speed(0)
        self.t.setpos(self.pos_x, self.pos_y)
        match self.rodzaj:
            case "zaopatrzenie":
                self.t.pendown()
                self.t.dot(20, "gold")
            case "przeciwnik":
                self.t.pendown()
                self.t.showturtle()
                self.t.dot(20, "red")
            case _:
                print("zly objekt")

    def get_pos(self):
        return [self.pos_x, self.pos_y]

    def set_pos(self, new_pos):
        self.pos_x = new_pos[0]
        self.pos_y = new_pos[1]
        self.t.speed(0)
        self.t.goto(new_pos)

    def get_id(self):
        return self.idx

    def get_rot(self):
        return self.kat

    def usun(self, cent):
        self.t.clear()
        match self.rodzaj:
            case "zaopatrzenie":
                cent.zmniejsz_zaopatrzenie()
                print(f"pozostałe zaopatrzenie: {cent.ilosc_zaopatrzenia}")
            case "przeciwnik":
                global numer_kroku
                global zdarzenia
                cent.old_pol = cent.polaczenie
                cent.polaczenie -= 10
                self.set_pos((random.uniform(-250, 250), random.uniform(-250, 250)))
                print("Przeciwnik zakłócił połączenie: -10")
                zdarzenia.append([numer_kroku, "ATAK PRZECIWNIKA"])

    def move(self, gracz, rozmiar):
        self.t.speed(0)
        war = get_angle_and_distance(self, [gracz], rozmiar)

        if war[1] < 75:
            distance = war[1]
            rozproszenie = 0
            print(f"{txt_eff['RED']}!!! WRÓG WYKONUJE ZRYW !!!{txt_eff['RESET']} (wrog w odległości mniejszej od 75)")
            input("wcisnij [ENTER] aby kontynuowac")

        elif war[1] <= 200:
            distance = 40
            rozproszenie = random.uniform(-15, 15)

        elif war[1] <= 300:
            distance = 55
            rozproszenie = random.uniform(-45, 45)

        else:
            distance = random.uniform(60, 80)
            rozproszenie = random.uniform(-90, 90)


        nowy_kat = war[0]
        self.kat -= nowy_kat + rozproszenie
        self.pos_x += round(math.cos(math.radians(self.kat)) * distance, 2)
        self.pos_y += round(math.sin(math.radians(self.kat)) * distance, 2)
        self.t.clear()
        self.t.speed(0)
        self.t.goto(self.pos_x, self.pos_y)
        self.t.dot(20, "red")


def wlacz_ansi():
    if platform.system() == "Windows":
        os.system("")


def wyczysc_ekran():
    os.system('cls' if os.name == 'nt' else 'clear')

def stop():
    global RUN
    RUN = False

RUN = True
if __name__ == '__main__':
    wlacz_ansi()
    wyczysc_ekran()

    print(f"{txt_eff['GREEN']}WYBIERZ POZIOM TRUDNOŚCI:{txt_eff['RESET']}")
    print(f"1. {txt_eff['CYAN']}Łatwy{txt_eff['RESET']}      (1 Przeciwnik )")
    print(f"2. {txt_eff['GREEN']}Średni{txt_eff['RESET']}     (2 Przeciwników)")
    print(f"3. {txt_eff['YELLOW']}Trudny{txt_eff['RESET']}     (3 Przeciwników)")
    print(f"4. {txt_eff['RED']}Ekstremalny{txt_eff['RESET']} (4 Przeciwników)")

    wybor = input(f"{txt_eff['PURPLE']}Wybór (1-4): {txt_eff['RESET']}")

    ilosc_zaopatrzenia = 5
    ilosc_wrogow = 2
    sugestia_polaczenia = 100

    match wybor:
        case "1":
            ilosc_wrogow = 1
            sugestia_polaczenia = 50
        case "2":
            ilosc_wrogow = 2
            sugestia_polaczenia = 60
        case "3":
            ilosc_wrogow = 3
            sugestia_polaczenia = 80
        case "4":
            ilosc_wrogow = 4
            sugestia_polaczenia = 100
        case _:
            print("Niepoprawny wybór, ustawiono poziom Średni.")
            input("wcisnij [ENTER] aby kontynuowac")

    wyczysc_ekran()

    swiat = SWIAT(500, ilosc_wrogow, ilosc_zaopatrzenia)

    nazwa_misji = input(f"{txt_eff['GREEN']}podaj nazwę misji (max: 50 znakow): {txt_eff['YELLOW']}")
    if len(nazwa_misji) > 50:
        nazwa_misji = nazwa_misji[:50]
    wyczysc_ekran()

    nazwa = input(f"{txt_eff['GREEN']}podaj nazwę postaci (max: 10 znakow): {txt_eff['YELLOW']}")
    if len(nazwa) > 10:
        nazwa = nazwa[:10]
    wyczysc_ekran()

    pozycja_x = input(f"{txt_eff['GREEN']}podaj startowy x (-250 - 250): {txt_eff['YELLOW']}")
    pozycja_y = input(f"{txt_eff['GREEN']}podaj startowy y (-250 - 250): {txt_eff['YELLOW']}")
    try:
        pozycja_x = clamp(int(pozycja_x), -250, 250)
        pozycja_y = clamp(int(pozycja_y),-250,250)
    except ValueError:
        print("zle parametry")
        pozycja_x, pozycja_y = 0, 0
    wyczysc_ekran()

    start_kat = input(f"{txt_eff['GREEN']}podaj kąt (-180 - 180): {txt_eff['YELLOW']}")
    try:
        start_kat = -clamp(int(start_kat),-180,180)
    except ValueError:
        print("zle parametry")
        start_kat = 0
    wyczysc_ekran()



    pol = input(f"{txt_eff['GREEN']}podaj poczatkowe połączenie (20 - 100)[Sugerowana dla poziomu: {sugestia_polaczenia}]: {txt_eff['YELLOW']}")
    try:
        pol = clamp(int(pol),20,100)
    except ValueError:
        print("zle parametry")
        pol = 100
    wyczysc_ekran()

    postac = GRACZ(nazwa, pozycja_x, pozycja_y, start_kat, pol, ilosc_zaopatrzenia)

    print(f"{txt_eff['GREEN']}{txt_eff['ITALIC']}Jesteś zwiadowcą który opuszcza bunkier w misji o nr {txt_eff['BOLD']}{txt_eff['PURPLE']}1048596{txt_eff['RESET']}{txt_eff['GREEN']}{txt_eff['ITALIC']}\n"
          f"Twoim zadaniem jest znalezienie porzuconego zaopatrzenia w okolicy \nunikając wrogich ataków oraz nie tracąc połączenia z bazą")
    input("\n\nwcisnij [ENTER] aby kontynuowac")
    wyczysc_ekran()
    a = ""
    b = 0
    numer_kroku = 1

    while a != "q":
        event = random.randint(0, 100)
        if event < 10:
            print(f"{txt_eff['YELLOW']}NIESPODZIEWANA BURZA PIASKOWA {txt_eff['RESET']} (losowa zmiana pozycji gracza)")
            postac.set_pos((random.uniform(-250,250), random.uniform(-250,250)))
            zdarzenia.append([numer_kroku, "BURZA PIASKOWA"])
            input()
        elif event < 35:
            dod = random.randint(3, 10)
            print(f"{txt_eff['YELLOW']}ZNALAZŁEŚ WZMACNIACZ SYGNAŁU {txt_eff['RESET']} (zwiększa połączenie o losową liczbę z zakresu (3 - 10)")
            postac.old_pol = postac.polaczenie
            postac.polaczenie += dod
            zdarzenia.append([numer_kroku, "WZMACNIACZ"])
            input()
        elif event < 50:
            odj = random.randint(1, 5)
            print(f"{txt_eff['YELLOW']}NIESPODZIEWANE ZAKŁÓCENIA {txt_eff['RESET']} (zmniejsza połączenie o losową liczbę z zakresu (1 - 5)")
            postac.old_pol = postac.polaczenie
            postac.polaczenie -= odj
            zdarzenia.append([numer_kroku, "ZAKŁÓCENIA"])
            input()
        else:
            pass

        raport_arr.append([numer_kroku, postac.get_pos(), postac.get_rot(), postac.polaczenie])

        if abs(postac.get_pos()[0]) > swiat.rozmiar//2 or abs(postac.get_pos()[1]) > swiat.rozmiar//2:
            input(f"{txt_eff['PURPLE']}MISJA NIEUDANA: WYSZEDŁEŚ POZA GRANICE ŚWIATA\n")
            break
        elif postac.polaczenie <= 0:
            input(f"{txt_eff['PURPLE']}MISJA NIEUDANA: STRACIŁEŚ POŁĄCZENIE\n")
            break

        print(f"{txt_eff['RED']}MISJA: {txt_eff['PURPLE']}{nazwa_misji}"
              f"{txt_eff['CYAN']}\nKROK NR: {numer_kroku}{txt_eff['RESET']}")
        postac.wypisz_wartosci()
        ang_dist = get_angle_and_distance(postac, swiat.objekty, swiat.rozmiar)

        print(f"{txt_eff['CYAN']}Najbliższy cel:\nkąt: {round(ang_dist[0], 2)}, Dystans: {round(ang_dist[1], 2)}, Status: {ang_dist[2]}")
        if not RUN:
            wyczysc_ekran()
            print(f"{txt_eff['PURPLE']}MISJA UDANA: ZEBRAŁES CAŁE ZAOPATRZENIE\n")
            break
        a = input(f"{txt_eff['YELLOW']}alfa (-180 - 180): {txt_eff['RESET']}")
        b = input(f"{txt_eff['YELLOW']}dystans (0 - 50): {txt_eff['RESET']}")
        if not a or a.isspace(): a = 0.0
        if not b or b.isspace(): b = 50
        wyczysc_ekran()
        try:
            postac.obrot(clamp(float(a),-180,180))
            postac.ruch(clamp(int(b),0,50))
            postac.old_pol = postac.polaczenie
            postac.polaczenie -= 1
        except ValueError:
            print(f"{txt_eff['RED']}zla wartość kata lub dystansu{txt_eff['RESET']}")

        for ob in swiat.objekty:
            if ob.rodzaj == "przeciwnik":
                ob.move(postac, swiat.rozmiar)

        numer_kroku += 1

print("RAPORT KOŃCOWY:\n\n")
print(f"{txt_eff['PURPLE']}{'NR KROKU':<12}{'POZYCJA (x, y)':<20}{'OBROT':<12}{'POŁĄCZENIE'}")
print("-" * 55)

for line in raport_arr:
    print(f"{line[0]:<12}{round(line[1][0], 2):<9}{round(line[1][1], 2):<12}{round(line[2], 2):<12}{line[3]}")

print(f"\n\n{txt_eff['CYAN']}{'NR KROKU':<12}{'ZDARZENIE'}")
print("-" * 25)

for line in zdarzenia:
    print(f"{line[0]:<12}{line[1]}")


