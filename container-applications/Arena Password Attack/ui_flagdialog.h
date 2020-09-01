/********************************************************************************
** Form generated from reading UI file 'flagdialog.ui'
**
** Created by: Qt User Interface Compiler version 5.15.0
**
** WARNING! All changes made in this file will be lost when recompiling UI file!
********************************************************************************/

#ifndef UI_FLAGDIALOG_H
#define UI_FLAGDIALOG_H

#include <QtCore/QVariant>
#include <QtWidgets/QApplication>
#include <QtWidgets/QDialog>
#include <QtWidgets/QLineEdit>

QT_BEGIN_NAMESPACE

class Ui_FlagDialog
{
public:
    QLineEdit *FlagDisplay;

    void setupUi(QDialog *FlagDialog)
    {
        if (FlagDialog->objectName().isEmpty())
            FlagDialog->setObjectName(QString::fromUtf8("FlagDialog"));
        FlagDialog->resize(500, 180);
        FlagDialog->setMinimumSize(QSize(500, 180));
        FlagDialog->setMaximumSize(QSize(500, 180));
        QFont font;
        font.setFamily(QString::fromUtf8("DS-Digital"));
        font.setPointSize(36);
        FlagDialog->setFont(font);
        FlagDisplay = new QLineEdit(FlagDialog);
        FlagDisplay->setObjectName(QString::fromUtf8("FlagDisplay"));
        FlagDisplay->setGeometry(QRect(10, 10, 480, 160));
        FlagDisplay->setMinimumSize(QSize(480, 160));
        FlagDisplay->setMaximumSize(QSize(480, 160));
        QFont font1;
        font1.setPointSize(36);
        FlagDisplay->setFont(font1);

        retranslateUi(FlagDialog);

        QMetaObject::connectSlotsByName(FlagDialog);
    } // setupUi

    void retranslateUi(QDialog *FlagDialog)
    {
        FlagDialog->setWindowTitle(QCoreApplication::translate("FlagDialog", "Dialog", nullptr));
        FlagDisplay->setText(QCoreApplication::translate("FlagDialog", " CyberGym{Pin_Test}", nullptr));
    } // retranslateUi

};

namespace Ui {
    class FlagDialog: public Ui_FlagDialog {};
} // namespace Ui

QT_END_NAMESPACE

#endif // UI_FLAGDIALOG_H
