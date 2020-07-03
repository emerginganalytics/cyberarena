#include "flagdialog.h"
#include "ui_flagdialog.h"

FlagDialog::FlagDialog(QWidget *parent) :
    QDialog(parent),
    ui(new Ui::FlagDialog)
{
    ui->setupUi(this);

    // Set Dialog Background:
    // Set Background image of application
    QPixmap bkgnd(":/Images/Icons/background.png");
    bkgnd = bkgnd.scaled(this->size(), Qt::IgnoreAspectRatio);
    QPalette palette;
    palette.setBrush(QPalette::Background, bkgnd);
    this->setPalette(palette);
}

FlagDialog::~FlagDialog()
{
    delete ui;
}
