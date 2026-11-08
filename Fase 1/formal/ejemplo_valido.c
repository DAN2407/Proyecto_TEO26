// programa de prueba
int x = 2;
int suma = 0;

while (x < 10) {
    suma = suma + x;
    x = x * 2;
}

if (suma > 5 && x != 0) {
    suma = suma - 1;
} else if (suma == 0) {
    suma = 1;
} else {
    suma = 0;
}