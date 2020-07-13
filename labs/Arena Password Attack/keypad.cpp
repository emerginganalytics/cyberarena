#include "keypad.h"
#include "ui_keypad.h"
#include "flagdialog.h"

Keypad::Keypad(QWidget *parent)
    : QMainWindow(parent)
    , ui(new Ui::Keypad)
{
    ui->setupUi(this);

    /* Set up and store PIN in a vector for easy access when
    *   establishing icon background.
    */
    setPin();

    /* Set Background image of application */
    QPixmap bkgnd(":/Images/Icons/background.png");
    bkgnd = bkgnd.scaled(this->size(), Qt::IgnoreAspectRatio);
    QPalette palette;
    palette.setBrush(QPalette::Background, bkgnd);
    this->setPalette(palette);

    /*
     * Get List of Number Keys/Key Press signals
     * Establish connection to the appropriate
     * keys 0-9
    */
    QPushButton *keyButtons[10];
    std::vector<int> pin_vector = Keypad::stored_pin;
    for (int i = 0; i < 10; ++i)
    {
       /* Check if current digit is part of the PIN;
        * If digit exists in PIN, set Icon to Worn
        * icon set,
        */
       std::vector<int>::iterator it = std::find(pin_vector.begin(), pin_vector.end(), i);
       QString keyName = "button_" + QString::number(i);
       keyButtons[i] = Keypad::findChild<QPushButton *>(keyName);
       if (it != pin_vector.end())
       {
           QPixmap icon_str = ":/Icons/Keys/Worn/Icons/Worn/number_0" +
                       QString::number(i) + "_worn.png";
           keyButtons[i]->setIcon(icon_str);
       }
       else {
           QPixmap icon_str = ":/Icons/Keys/New/Icons/New/number_0" +
                       QString::number(i) + "_new.png";
           keyButtons[i]->setIcon(icon_str);
       }
       /* Establish GUI connection for each button */
       connect(keyButtons[i], SIGNAL(released()), this,
               SLOT(keyPressed()));
    }
    /* Set up GUI connection for Enter key */
    connect(ui->Enter, SIGNAL(released()), this,
            SLOT(login()));
}

Keypad::~Keypad()
{
    delete ui;
}

void
Keypad::setPin()
{
    /*
        This function will take a vector of the possible numbers
        0-9 and randomly select 4 digits and set the private
        variable, pin equal to those for numbers in string form.
    */
    std::vector<int> numbers = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9};
    std::srand(time(NULL));
    bool duplicate;

    for (int i = 0; i < 4; i++)
    {
        do {
            std::vector<int> pin_vector = Keypad::stored_pin;
            int pin_vSize = numbers.size();
            int index = rand() % pin_vSize;
            int digit = numbers[index];

            if (std::find(pin_vector.begin(), pin_vector.end(), digit) != pin_vector.end())
            {
                /* Duplicate is found. Retry generate number */
                duplicate = true;
            }
            else {
                /* No duplicate is found. Safe to add to stored_pin */
                Keypad::pin += QString::number(digit);
                Keypad::stored_pin.push_back(digit);

                duplicate = false;
            }
        } while (duplicate);
    }
    qDebug() << Keypad::pin;
    qDebug() << Keypad::stored_pin;
    qDebug() << Keypad::stored_pin.size();
}

void
Keypad::keyPressed()
{
    /*
    * This function handles each buttonclick event. It takes
    * the object name and determines the appropriate value
    * for each button based on the value to the right of the
    * _ character.
    * We split objectName into a StringList at the underscore.
    * Set value for pressed button equal to the last value
    * in the StringList.
    *
    * Example: button_5 is parsed to ['button', '5']
    *         keyValue = buttonElements[1] = '5'
    *
    * The display is then updated with the new value appended
    * to the Keypad display. To simplify the workout, we
    * restrict PIN size to 4 digits. If more than 4 digits
    * are entered, we keep only the first 4 entries.
    *
    */
    QPushButton *button = (QPushButton *)sender();
    QString displayVal = ui->Display->text();
    QVector<int> display_vector = {};

    QString buttonName = button->objectName();
    QStringList buttonElements = buttonName.split("_");
    QString keyValue = buttonElements[1];

    /*  First we need to clear the greeting if it's there.
     *  If the first character in the string array, displayVal
     *  is a letter, we can assume the remaining characters are
     *  letters and discard them.
     */
    if (!displayVal.isEmpty() && displayVal[0].isLetter()) {
        ui->Display->setText(keyValue);
    }
    /* Restrict inputs to be only 4 characters in length */
    else if (displayVal.length() >= 4){
        ui->Display->setText(displayVal);
    }
    /* Otherwise, keep adding key values to displayVal */
    else {
        QString newVal = displayVal + keyValue;
        ui->Display->setText(newVal);
    }
}

void
Keypad::login()
{
    /*
     * login() is called whenever the Enter button
     * event is triggerred.
     * We take the display text and
     * convert it to an int before comparing with
     * the stored PIN.
     * If the PIN's are equivalent,
     * we update the display, open the flag dialog,
     * and call the post() function.
     * If the PINs don't match, we simply clear the
     * display.
     */
    QString check = Keypad::pin; //.toInt();
    QString displayValue = ui->Display->text();
    int pin = displayValue.toInt();

    // Initialize Flag Dialog
    FlagDialog *dialog = new FlagDialog;

    // if enter key is pressed, compare pins
   if (pin == check.toInt()){
       QFont font = ui->Display->font();
       font.setPointSize(40);
       ui->Display->setFont(font);
       ui->Display->setText("SUCCESS!");

       // pop up dialog box with flag and then post to URL
       dialog->show();
       /* This will be used in later versions for auto-assessment */
       // post();
     }
   else {
       // Pop dialog box of login failed
       ui->Display->setText("");
   }
}

void
Keypad::post()
{
    /*  [ CURRENTLY NOT WORKING ]
     * post() is called at workout completion. This utilizes
     * the Qt Network and QJson libraries to call the Qt cURL
     * wrapper and POST to the appropriate URL with the
     * environment variables WORKOUTID and WORKOUTKEY attached
     * as a JSON object.
    */
    QString WORKOUTID = std::getenv("WORKOUTID0");
    QString WORKOUTKEY = std::getenv("WORKOUTKEY0");

    QUrl URL("https://buildthewarrior.cybergym-eac-ualr.org/complete");
    QNetworkRequest request(URL);

    // JSON Object with key:value of {workout_id:WORKOUTID, tokent:WORKOUTKEY}
    request.setHeader(QNetworkRequest::ContentTypeHeader, "application/json");
    // Initialize the QNetwork object
    QJsonObject jsnObj;
    jsnObj.insert("workout_id", QJsonValue::fromVariant(WORKOUTID));
    jsnObj.insert("token", QJsonValue::fromVariant(WORKOUTKEY));

    QJsonDocument doc(jsnObj);
    qDebug() << jsnObj;
    qDebug() << doc.toJson();
    QNetworkAccessManager manager;
    QNetworkReply *reply = manager.post(request, doc.toJson());

    while(!reply->isFinished())
    {
        qApp->processEvents();
    }
    QByteArray response = reply->readAll();
    reply->deleteLater();
}
