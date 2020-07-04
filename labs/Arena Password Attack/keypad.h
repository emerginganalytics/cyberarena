/*
 * ################ LIBRARIES USED: ####################
 *   QPixmap and QPainter are used for setting the
 *   background image for both Keypad and FlagDialog
 *
 *   cstdlib is how what we use to pull environment
 *   variables in order to update the correct
 *   assessment question.
 *
 *   QNetworkAccessManager is the QT library/wrapper
 *   for cURL. Used to POST to URL.
 *
 *   QJsonObject helps encapsulate the appropriate data
 *   for the cURL POST request
 *  #####################################################
*/
#ifndef KEYPAD_H
#define KEYPAD_H

#include <QMainWindow>
#include <QPixmap>             /* Handling images */
#include <QPainter>
#include <QJsonArray>          /* Handling POST Requests */
#include <QJsonDocument>
#include <QJsonObject>
#include <QJsonValue>
#include <QNetworkAccessManager>
#include <QNetworkRequest>
#include <QNetworkReply>
#include <QVariant>
#include <QDebug>
#include <cstdlib>            /* Pulling ENV variables */
#include <string>

QT_BEGIN_NAMESPACE
namespace Ui { class Keypad; }
QT_END_NAMESPACE

class Keypad : public QMainWindow
{
    Q_OBJECT

public:
    Keypad(QWidget *parent = nullptr);
    ~Keypad();

private:
    Ui::Keypad *ui;
    void post();

private slots:
    void keyPressed();
    void login();
};
#endif // KEYPAD_H
