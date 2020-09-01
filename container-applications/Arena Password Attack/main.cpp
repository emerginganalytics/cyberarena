#include "keypad.h"
#include "flagdialog.h"

#include <QApplication>
#include <QLineEdit>
#include <QRegExpValidator>

int main(int argc, char *argv[])
{
    /*
     * This application will run a simple Keypad GUI
     * to provide a realistic demonstration of brute-
     * forcing keypads. Students can guess the PIN
     * by observing which keys appear to be worn.
     *
     * Currently, this is a static workout, but it
     * is possible to add functionality to dynamically
     * create the PIN and update the appropriate key
     * backgrounds using vectors and the QPixMap
     * library.
     */
    QApplication a(argc, argv);

    /* Initialize Keypad */
    Keypad w;
    w.show();
    /* Limit Keypad inputs to submit only digits 0-9 */
    QLineEdit display;
    display.setValidator(new QRegExpValidator(QRegExp("[0-9]*"), &display));

    return a.exec();
}
