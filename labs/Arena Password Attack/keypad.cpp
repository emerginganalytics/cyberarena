#include "keypad.h"
#include "ui_keypad.h"
#include "flagdialog.h"

int displayVal = 0;

Keypad::Keypad(QWidget *parent)
    : QMainWindow(parent)
    , ui(new Ui::Keypad)
{
    ui->setupUi(this);

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
    ui->Display->setText(QString::number(displayVal));
    QPushButton *keyButtons[10];
    for (int i = 0; i < 10; ++i)
    {
       QString keyName = "button_" + QString::number(i);
       keyButtons[i] = Keypad::findChild<QPushButton *>(keyName);
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
Keypad::keyPressed()
{
    /*
    * This function handles each buttonclick event. It takes
    * the object name and determines the appropriate value
    * for each button. Since we are only handling 10 buttons,
    * a simple if-else conditional is sufficient.
    *
    * The display is then updated with the new value appended
    * to the Keypad display. To simplify the workout, we
    * restrict PIN size to 4 digits. If more than 4 digits
    * are entered, we keep only the first 4 entries.
    */
    QPushButton *button = (QPushButton *)sender();
    int keyValue;
    QString displayVal = ui->Display->text();

    // Set value for pressed button
    if (button->objectName() == "button_0"){
        keyValue = 0;
    }
    else if (button->objectName() == "button_1") {
        keyValue = 1;
    }
    else if (button->objectName() == "button_2") {
        keyValue = 2;
    }
    else if (button->objectName() == "button_3") {
        keyValue = 3;
    }
    else if (button->objectName() == "button_4") {
        keyValue = 4;
    }
    else if (button->objectName() == "button_5") {
        keyValue = 5;
    }
    else if (button->objectName() == "button_6") {
        keyValue = 6;
    }
    else if (button->objectName() == "button_7") {
        keyValue = 7;
    }
    else if (button->objectName() == "button_8") {
        keyValue = 8;
    }
    else if (button->objectName() == "button_9") {
        keyValue = 9;
    }
    // restrict inputs of more than 4 digits
    if (displayVal.length() == 4){
        ui->Display->setText(displayVal);
    }
    else {
        if((displayVal.toInt() == 0 || (displayVal.toInt() == 0))){
            ui->Display->setText(QString::number(keyValue));
        }
        else {
            QString newVal = displayVal + QString::number(keyValue);
            int newDisplay = newVal.toInt();
            ui->Display->setText(QString::number(newDisplay, 'g', 16));
        }
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
    int check = 5813;
    QString displayValue = ui->Display->text();
    int pin = displayValue.toInt();

    // Initialize Flag Dialog
    FlagDialog *dialog = new FlagDialog;

    // if enter key is pressed, compare pins
   if (pin == check){
       QFont font = ui->Display->font();
       font.setPointSize(40);
       ui->Display->setFont(font);
       ui->Display->setText("SUCCESS!");

       // pop up dialog box with flag and then post to URL
       dialog->show();
       /* This will be used in later versions for auto-assessment */
       post();
     }
   else {
       // Pop dialog box of login failed
       ui->Display->setText("");
   }
}

void
Keypad::post()
{
    /*
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
