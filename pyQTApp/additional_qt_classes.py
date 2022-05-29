from PyQt5 import QtWidgets, QtCore


class SpinBox(QtWidgets.QSpinBox):
    upClicked = QtCore.pyqtSignal()
    downClicked = QtCore.pyqtSignal()

    def mousePressEvent(self, event):
        print(f'self value = {self.objectName()}')
        last_value = self.value
        print(f'clicked old value = {last_value}')
        # super(SpinBox, self).mousePressEvent(event)
        super().mousePressEvent(event)
        print(f'clicked new value = {self.value}')
        if self.value <= last_value:
            self.downClicked.emit()
        elif self.value > last_value:
            self.upClicked.emit()

