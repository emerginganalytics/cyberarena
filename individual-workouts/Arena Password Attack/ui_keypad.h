/********************************************************************************
** Form generated from reading UI file 'keypad.ui'
**
** Created by: Qt User Interface Compiler version 5.15.0
**
** WARNING! All changes made in this file will be lost when recompiling UI file!
********************************************************************************/

#ifndef UI_KEYPAD_H
#define UI_KEYPAD_H

#include <QtCore/QVariant>
#include <QtGui/QIcon>
#include <QtWidgets/QApplication>
#include <QtWidgets/QLineEdit>
#include <QtWidgets/QMainWindow>
#include <QtWidgets/QPushButton>
#include <QtWidgets/QStatusBar>
#include <QtWidgets/QWidget>

QT_BEGIN_NAMESPACE

class Ui_Keypad
{
public:
    QWidget *centralwidget;
    QPushButton *button_0;
    QPushButton *Enter;
    QPushButton *button_1;
    QPushButton *button_2;
    QPushButton *button_3;
    QPushButton *button_4;
    QPushButton *button_5;
    QPushButton *button_6;
    QPushButton *button_7;
    QPushButton *button_8;
    QPushButton *button_9;
    QLineEdit *Display;
    QStatusBar *statusbar;

    void setupUi(QMainWindow *Keypad)
    {
        if (Keypad->objectName().isEmpty())
            Keypad->setObjectName(QString::fromUtf8("Keypad"));
        Keypad->setEnabled(true);
        Keypad->resize(350, 570);
        QSizePolicy sizePolicy(QSizePolicy::Preferred, QSizePolicy::Preferred);
        sizePolicy.setHorizontalStretch(0);
        sizePolicy.setVerticalStretch(0);
        sizePolicy.setHeightForWidth(Keypad->sizePolicy().hasHeightForWidth());
        Keypad->setSizePolicy(sizePolicy);
        Keypad->setMinimumSize(QSize(350, 570));
        Keypad->setMaximumSize(QSize(350, 570));
        Keypad->setBaseSize(QSize(350, 570));
        QFont font;
        font.setFamily(QString::fromUtf8("DS-Digital"));
        font.setPointSize(60);
        Keypad->setFont(font);
        Keypad->setWindowOpacity(1.000000000000000);
        Keypad->setStyleSheet(QString::fromUtf8("#QMainWindow {\n"
"	max-height: 550px;\n"
"}"));
        centralwidget = new QWidget(Keypad);
        centralwidget->setObjectName(QString::fromUtf8("centralwidget"));
        sizePolicy.setHeightForWidth(centralwidget->sizePolicy().hasHeightForWidth());
        centralwidget->setSizePolicy(sizePolicy);
        centralwidget->setMinimumSize(QSize(350, 550));
        centralwidget->setMaximumSize(QSize(350, 550));
        centralwidget->setBaseSize(QSize(350, 550));
        centralwidget->setStyleSheet(QString::fromUtf8(""));
        button_0 = new QPushButton(centralwidget);
        button_0->setObjectName(QString::fromUtf8("button_0"));
        button_0->setGeometry(QRect(30, 410, 81, 81));
        button_0->setStyleSheet(QString::fromUtf8("QPushButton { \n"
"	border-top: 3px white;\n"
"	border-bottom: 3px white;\n"
"	border-left: 3px white;\n"
"	border-right: 3px white;\n"
"}"));
        QIcon icon;
        icon.addFile(QString::fromUtf8(":/Icons/Keys/New/Icons/New/number_00_new.png"), QSize(), QIcon::Normal, QIcon::Off);
        button_0->setIcon(icon);
        button_0->setIconSize(QSize(84, 84));
        Enter = new QPushButton(centralwidget);
        Enter->setObjectName(QString::fromUtf8("Enter"));
        Enter->setGeometry(QRect(130, 430, 181, 61));
        Enter->setStyleSheet(QString::fromUtf8("QPushButton { \n"
"	border-top: 3px white;\n"
"	border-bottom: 3px white;\n"
"	border-left: 3px white;\n"
"	border-right: 3px white;\n"
"}"));
        QIcon icon1;
        icon1.addFile(QString::fromUtf8(":/Icons/Keys/Worn/Icons/Worn/keypad-enter.png"), QSize(), QIcon::Normal, QIcon::Off);
        Enter->setIcon(icon1);
        Enter->setIconSize(QSize(200, 200));
        button_1 = new QPushButton(centralwidget);
        button_1->setObjectName(QString::fromUtf8("button_1"));
        button_1->setGeometry(QRect(30, 320, 81, 81));
        button_1->setStyleSheet(QString::fromUtf8("QPushButton { \n"
"	border-top: 3px white;\n"
"	border-bottom: 3px white;\n"
"	border-left: 3px white;\n"
"	border-right: 3px white;\n"
"}\n"
"QAbstractButton {\n"
"	text-align: center;\n"
"}"));
        QIcon icon2;
        icon2.addFile(QString::fromUtf8(":/Icons/Keys/Worn/Icons/Worn/number_01_worn.png"), QSize(), QIcon::Normal, QIcon::Off);
        button_1->setIcon(icon2);
        button_1->setIconSize(QSize(84, 84));
        button_2 = new QPushButton(centralwidget);
        button_2->setObjectName(QString::fromUtf8("button_2"));
        button_2->setGeometry(QRect(130, 320, 81, 81));
        button_2->setStyleSheet(QString::fromUtf8("QPushButton { \n"
"	border-top: 3px white;\n"
"	border-bottom: 3px white;\n"
"	border-left: 3px white;\n"
"	border-right: 3px white;\n"
"}"));
        QIcon icon3;
        icon3.addFile(QString::fromUtf8(":/Icons/Keys/New/Icons/New/number_02_new.png"), QSize(), QIcon::Normal, QIcon::Off);
        button_2->setIcon(icon3);
        button_2->setIconSize(QSize(84, 84));
        button_3 = new QPushButton(centralwidget);
        button_3->setObjectName(QString::fromUtf8("button_3"));
        button_3->setGeometry(QRect(230, 320, 81, 81));
        button_3->setStyleSheet(QString::fromUtf8("QPushButton { \n"
"	border-top: 3px white;\n"
"	border-bottom: 3px white;\n"
"	border-left: 3px white;\n"
"	border-right: 3px white;\n"
"}"));
        QIcon icon4;
        icon4.addFile(QString::fromUtf8(":/Icons/Keys/Worn/Icons/Worn/number_03_worn.png"), QSize(), QIcon::Normal, QIcon::Off);
        button_3->setIcon(icon4);
        button_3->setIconSize(QSize(84, 84));
        button_4 = new QPushButton(centralwidget);
        button_4->setObjectName(QString::fromUtf8("button_4"));
        button_4->setGeometry(QRect(30, 230, 81, 81));
        button_4->setStyleSheet(QString::fromUtf8("QPushButton { \n"
"	border-top: 3px white;\n"
"	border-bottom: 3px white;\n"
"	border-left: 3px white;\n"
"	border-right: 3px white;\n"
"}"));
        QIcon icon5;
        icon5.addFile(QString::fromUtf8(":/Icons/Keys/New/Icons/New/number_04_new.png"), QSize(), QIcon::Normal, QIcon::Off);
        button_4->setIcon(icon5);
        button_4->setIconSize(QSize(84, 84));
        button_5 = new QPushButton(centralwidget);
        button_5->setObjectName(QString::fromUtf8("button_5"));
        button_5->setGeometry(QRect(130, 230, 81, 81));
        button_5->setStyleSheet(QString::fromUtf8("QPushButton { \n"
"	border-top: 3px white;\n"
"	border-bottom: 3px white;\n"
"	border-left: 3px white;\n"
"	border-right: 3px white;\n"
"}"));
        QIcon icon6;
        icon6.addFile(QString::fromUtf8(":/Icons/Keys/Worn/Icons/Worn/number_05_worn.png"), QSize(), QIcon::Normal, QIcon::Off);
        button_5->setIcon(icon6);
        button_5->setIconSize(QSize(84, 84));
        button_6 = new QPushButton(centralwidget);
        button_6->setObjectName(QString::fromUtf8("button_6"));
        button_6->setGeometry(QRect(230, 230, 81, 81));
        button_6->setStyleSheet(QString::fromUtf8("QPushButton { \n"
"	border-top: 3px white;\n"
"	border-bottom: 3px white;\n"
"	border-left: 3px white;\n"
"	border-right: 3px white;\n"
"}"));
        QIcon icon7;
        icon7.addFile(QString::fromUtf8(":/Icons/Keys/New/Icons/New/number_06_new.png"), QSize(), QIcon::Normal, QIcon::Off);
        button_6->setIcon(icon7);
        button_6->setIconSize(QSize(84, 84));
        button_7 = new QPushButton(centralwidget);
        button_7->setObjectName(QString::fromUtf8("button_7"));
        button_7->setGeometry(QRect(30, 140, 81, 81));
        button_7->setStyleSheet(QString::fromUtf8("QPushButton { \n"
"	border-top: 3px white;\n"
"	border-bottom: 3px white;\n"
"	border-left: 3px white;\n"
"	border-right: 3px white;\n"
"}"));
        QIcon icon8;
        icon8.addFile(QString::fromUtf8(":/Icons/Keys/New/Icons/New/number_07_new.png"), QSize(), QIcon::Normal, QIcon::Off);
        button_7->setIcon(icon8);
        button_7->setIconSize(QSize(84, 84));
        button_7->setAutoDefault(false);
        button_8 = new QPushButton(centralwidget);
        button_8->setObjectName(QString::fromUtf8("button_8"));
        button_8->setGeometry(QRect(130, 140, 81, 81));
        button_8->setStyleSheet(QString::fromUtf8("QPushButton { \n"
"	border-top: 3px white;\n"
"	border-bottom: 3px white;\n"
"	border-left: 3px white;\n"
"	border-right: 3px white;\n"
"}"));
        QIcon icon9;
        icon9.addFile(QString::fromUtf8(":/Icons/Keys/Worn/Icons/Worn/number_08_worn.png"), QSize(), QIcon::Normal, QIcon::Off);
        button_8->setIcon(icon9);
        button_8->setIconSize(QSize(84, 84));
        button_9 = new QPushButton(centralwidget);
        button_9->setObjectName(QString::fromUtf8("button_9"));
        button_9->setGeometry(QRect(230, 140, 81, 81));
        button_9->setStyleSheet(QString::fromUtf8("QPushButton { \n"
"	border-top: 3px white;\n"
"	border-bottom: 3px white;\n"
"	border-left: 3px white;\n"
"	border-right: 3px white;\n"
"}"));
        QIcon icon10;
        icon10.addFile(QString::fromUtf8(":/Icons/Keys/New/Icons/New/number_09_new.png"), QSize(), QIcon::Normal, QIcon::Off);
        button_9->setIcon(icon10);
        button_9->setIconSize(QSize(84, 84));
        Display = new QLineEdit(centralwidget);
        Display->setObjectName(QString::fromUtf8("Display"));
        Display->setGeometry(QRect(10, 20, 331, 101));
        QFont font1;
        font1.setFamily(QString::fromUtf8("DS-Digital"));
        font1.setPointSize(50);
        font1.setBold(false);
        font1.setItalic(false);
        font1.setWeight(50);
        Display->setFont(font1);
        Display->setStyleSheet(QString::fromUtf8("#Display {\n"
"	font: 50pt \"DS-Digital\";\n"
"	color: black;\n"
"	background-color: rgb(210, 255, 255);\n"
"}"));
        Display->setAlignment(Qt::AlignRight|Qt::AlignTrailing|Qt::AlignVCenter);
        Keypad->setCentralWidget(centralwidget);
        statusbar = new QStatusBar(Keypad);
        statusbar->setObjectName(QString::fromUtf8("statusbar"));
        Keypad->setStatusBar(statusbar);

        retranslateUi(Keypad);

        QMetaObject::connectSlotsByName(Keypad);
    } // setupUi

    void retranslateUi(QMainWindow *Keypad)
    {
        Keypad->setWindowTitle(QCoreApplication::translate("Keypad", "TOP SECRET", nullptr));
        button_0->setText(QString());
        Enter->setText(QString());
        button_1->setText(QString());
        button_2->setText(QString());
        button_3->setText(QString());
        button_4->setText(QString());
        button_5->setText(QString());
        button_6->setText(QString());
        button_7->setText(QString());
        button_8->setText(QString());
        button_9->setText(QString());
        Display->setText(QCoreApplication::translate("Keypad", "Enter Pin", nullptr));
    } // retranslateUi

};

namespace Ui {
    class Keypad: public Ui_Keypad {};
} // namespace Ui

QT_END_NAMESPACE

#endif // UI_KEYPAD_H
