from math import sqrt
from tkinter import *
from PIL import ImageTk, Image
from tkinter.filedialog import askopenfilename
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg)


# Wybór obrazu do przetworzenia.
def wybierz_plik():
    global img_original_label, image, img_original
    label_error.config(text="")
    filetypes = (('imgs', '*.png *.jpg *.jpeg'),)
    filename = askopenfilename(title='Wybierz obraz do klasyfikacji', filetypes=filetypes)
    try:
        image = Image.open(filename)
    except:
        pass
    else:
        image = image.resize((round(396 / image.size[1] * image.size[0]/3)*3, 396))
        if image.size[0] > 864:
            image = image.resize((864, round(864 / image.size[0] * image.size[1]/3)*3))
        img_original = ImageTk.PhotoImage(image)
        img_original_label.destroy()
        img_classified_label.destroy()
        img_original_label = Label(image=img_original)
        img_original_label.place(x=5, y=5)


# Przetwarzanie obrazu.
def start():
    global image, img_classified, img_classified_label, arr_of_avgs, label_error
    try:
        image
    except:
        label_error = Label(root, text="Najpierw musisz wybrać obraz!", bg="white")
        label_error.place(x=1300, y=10)
    else:
        arr_of_avgs = np.zeros((image.size[1], image.size[0]))
        i = 0
        while i < image.size[0]:
            j = 0
            while j < image.size[1]:
                avg = group_pixels(i, j)
                chosen = find_closest_color(avg)
                assign_pixel(chosen, i, j, arr_of_avgs, avg)
                j += 3
            i += 3
        img_classified = ImageTk.PhotoImage(image)
        img_classified_label = Label(image=img_classified)
        img_classified_label.place(x=5, y=400)
        root.bind("<Button 1>", print_details)


def draw_plot(xp, yp, zp, xpr, ypr, zpr):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    for i in range(num):
        ax.plot(xpr[i], ypr[i], zpr[i], color='r')
    ax.plot(xp, yp, zp, color='g')
    ax.set_xlabel("RED")
    ax.set_ylabel("GREEN")
    ax.set_zlabel("BLUE")
    ax.set_xlim(0, 255)
    ax.set_ylim(0, 255)
    ax.set_zlim(0, 255)
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.draw()
    canvas.get_tk_widget().place(x=870, y=320)


def print_details(event):
    xr = event.x_root - 2
    x = event.x - 2
    y = event.y - 2
    if 870 > xr >= 5 and x < image.size[0] and image.size[1] > y >= 0:
        # Canvas zawierający dane o klasach i klikniętym pikselu.
        canvas = Canvas(root, height=200, width=660, bg="#ffffff", highlightthickness=0)
        canvas.place(x=870, y=125)
        # xpr,ypr,zpr[num][0] - współrzędne (R,G,B) dla klikniętego piksela
        # xpr,ypr,zpr[num][1] - współrzędne (R,G,B) klasy o indeksie 'num'
        xpr = np.zeros((num, 2))
        ypr = np.zeros((num, 2))
        zpr = np.zeros((num, 2))
        for i in range(num):
            xpr[i][1] = int(classes[i] / 256 / 256 % 256)
            ypr[i][1] = int(classes[i] / 256 % 256)
            zpr[i][1] = int(classes[i] % 256)
            xpr[i][0] = int(arr_of_avgs[y][x] / 256 / 256 % 256)
            ypr[i][0] = int(arr_of_avgs[y][x] / 256 % 256)
            zpr[i][0] = int(arr_of_avgs[y][x] % 256)
            dist = (xpr[i][1] - xpr[i][0]) ** 2 + (ypr[i][1] - ypr[i][0]) ** 2 + (zpr[i][1] - zpr[i][0]) ** 2
            dist = sqrt(dist)
            # Dane poszczególnych klas i odległości między nimi a klikniętym pikselem.
            colorval = "#%0.6X" % int(classes[i])
            canvas.create_rectangle(45+130*i, 10, 85+130*i, 50, outline="#ffffff", fill=colorval)
            canvas.create_text(65+130*i, 61, fill="black", font="Times 7", text="Klasa " + str(i))
            canvas.create_text(65+130*i, 72, fill="black", font="Times 7",
                               text="RGB: (" + str(int(xpr[i][1])) + ", " + str(int(ypr[i][1])) + ", " + str(int(zpr[i][1])) + ")")
            canvas.create_text(65+130*i, 83, fill="black", font="Times 7", text="Obliczona odległość: " + str("{:.2f}".format(dist)))
            if image.getpixel((x, y)) == (xpr[i][1], ypr[i][1], zpr[i][1]):
                choice = i
        # xp,yp,zp[0] - współrzędne (R,G,B) dla klikniętego piksela
        # xp,yp,zp[1] - współrzędne (R,G,B) przypisanej klasy dla tego piksela
        xp = np.zeros(2)
        yp = np.zeros(2)
        zp = np.zeros(2)
        xp[0] = int(arr_of_avgs[y][x] / 256 / 256 % 256)
        yp[0] = int(arr_of_avgs[y][x] / 256 % 256)
        zp[0] = int(arr_of_avgs[y][x] % 256)
        xp[1], yp[1], zp[1] = image.getpixel((x, y))
        # Dane klikniętego piksela.
        colorval = "#%0.6X" % int(arr_of_avgs[y][x])
        canvas.create_rectangle(45, 100, 85, 140, outline="#ffffff", fill=colorval)
        canvas.create_text(65, 151, fill="black", font="Times 7", text="Średnia wartość RGB")
        canvas.create_text(65, 162, fill="black", font="Times 7", text="dla wybranego piksela:")
        canvas.create_text(65, 173, fill="black", font="Times 7", text="(" + str(int(xp[0])) + ", " + str(int(yp[0])) + ", " + str(int(zp[0])) + ")")
        # Dane wybranej klasy.
        colorval = "#%02x%02x%02x" % (int(xp[1]), int(yp[1]), int(zp[1]))
        canvas.create_rectangle(175, 100, 215, 140, outline="#ffffff", fill=colorval)
        canvas.create_text(195, 150, fill="black", font="Times 7", text="Wybrana klasa: " + str(choice) + ".")
        draw_plot(xp, yp, zp, xpr, ypr, zpr)


# Grupowanie kwadratu 3x3 pikseli i uśrednienie ich wartości r, g, b. Zwraca listę uśrednionych wartości r, g, b.
def group_pixels(i, j):
    avg = np.zeros(3)
    for k in range(3):
        for l in range(3):
            r, g, b = image.getpixel((i + k, j + l))
            avg[0] += r
            avg[1] += g
            avg[2] += b
    avg[0] /= 9
    avg[1] /= 9
    avg[2] /= 9
    return avg


# Znajduje kolor najbliższy do koloru o wartościach r, g, b zawartych w liście wejściowej.
# Zwraca numer indeksu dopasowanej klasy.
def find_closest_color(avg):
    closest = 0
    chosen = 0
    for k in range(num):
        current = calculate_distance(avg, k)
        if k == 0:
            closest = calculate_distance(avg, 0)
        elif current < closest:
            closest = calculate_distance(avg, k)
            chosen = k
    return chosen


# Przypisuje do piksela o wymiarach i, j wartości r, g, b odpowiednio obliczone z elementu listy klas o indeksie chosen.
# Elementy w tablicy klas (classes) są typu int, więc obliczane są wartości r, g, b.
def assign_pixel(chosen, i, j, arr_of_avgs, avg):
    for k in range(3):
        for l in range(3):
            arr_of_avgs[j+l][i+k] = int(avg[0])*256*256+int(avg[1])*256+int(avg[2])
            r = int(classes[chosen] / 256 / 256) % 256
            g = int(classes[chosen] / 256) % 256
            b = int(classes[chosen] % 256)
            image.putpixel((i + k, j + l), (r, g, b))


# Oblicza kwadrat odległości między punktami w przestrzeni trójwymiarowej
# (bez pierwiastka, gdyż nie jest potrzebny dla porównania).
# avg to punkt o współrzędnych (R,G,B) (uśrednione wartości z dziewięciu pikseli)
# k jest numerem indeksu w tablicy klas
def calculate_distance(avg, k):
    r = int(classes[k]/256/256 % 256)
    g = int(classes[k]/256 % 256)
    b = int(classes[k] % 256)
    dist = (int(avg[0]) - r) ** 2 + (int(avg[1]) - g) ** 2 + (int(avg[2]) - b) ** 2
    return dist


# liczba klas
num = 5
classes = np.zeros(num)
# dark green (green terrain, forest)
classes[0] = 0x27553b
# dark blue (water)
classes[1] = 0x003437
# light yellow (sand)
classes[2] = 0xB8A877
# grey (buildings_1)
classes[3] = 0x706C63
# light grey (buildings_2)
classes[4] = 0xC8C5C0

root = Tk()
label_error = Label(root)
root.geometry("1500x700")
root.title('Klasyfikacja obrazów')
root.configure(background='white')
canvas = Canvas(root, height=130, width=660, bg="#fff", highlightthickness=0)
canvas.place(x=870, y=5)
canvas.create_text(
    330, 60,
    fill="black",
    font="Times 9",
    text="Zasada działania programu:\n1. Wybór pliku i rozpoczęcie klasyfikacji obrazu.\n" +
        "2. Uśrednianie wartości RGB dziewięciu sąsiadujących pikseli (z kwadratu 3x3).\n" +
        "3. Wybór klasy reprezentującej najbardziej podobny kolor do uzyskanego koloru uśrednionego, poprzez obliczenie odległości\n" +
        "    między uśrednionym punktem o współrzędnych (R,G,B) a punktem (R,G,B) reprezentującym klasę.\n" +
        "4. Przypisanie do dziewięciu pikseli wartości RGB klasy, której odległość od punktu uśrednionego jest najmniejsza.\n" +
        "5. Powtórzenie operacji 2-4 dla kolejnej grupy dziewięciu pikseli.\n" +
        "6. Po wyświetleniu sklasyfikowanego obrazu, możliwe jest wybranie piksela, w celu informacji o odległościach od poszczególnych klas.")
button_plik = Button(root, text="Wybierz plik", width=10, command=wybierz_plik)
button_plik.place(x=1130, y=5)
button_start = Button(root, text="Start", width=5, command=start)
button_start.place(x=1230, y=5)
img_original_label = Label()
img_classified_label = Label()
root.state('zoomed')

root.mainloop()
