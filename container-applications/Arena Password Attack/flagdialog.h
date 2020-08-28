#ifndef FLAGDIALOG_H
#define FLAGDIALOG_H

#include <QDialog>

namespace Ui {
class FlagDialog;
}

class FlagDialog : public QDialog
{
    Q_OBJECT

public:
    explicit FlagDialog(QWidget *parent = nullptr);
    ~FlagDialog();

private:
    Ui::FlagDialog *ui;
};

#endif // FLAGDIALOG_H
