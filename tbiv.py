import os
import os.path
import sys

from PyQt4 import QtGui, QtCore


class MainWindow(QtGui.QFrame):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('TBIV')

        layout = QtGui.QHBoxLayout(self)
        self.img_list = QtGui.QListWidget()
        self.img_list.setViewMode(QtGui.QListWidget.IconMode)
        self.img_list.setMovement(QtGui.QListWidget.Static)
        self.img_list.setUniformItemSizes(True)
        self.img_list.setBatchSize(10)
        self.img_list.setLayoutMode(QtGui.QListWidget.Batched)
        self.img_list.setIconSize(QtCore.QSize(100,100))
        self.img_list.setResizeMode(QtGui.QListWidget.Adjust)
        path = r'.'
        self.show_directory(self.img_list, path)
        layout.addWidget(self.img_list)
        self.show()
        self.resize(1024,768)

    def show_directory(self, list_widget, path):
        tpool = QtCore.QThreadPool.globalInstance()
        tempimg = QtGui.QPixmap(100, 100)
        tempimg.fill()
        for n,f in enumerate([f for f in os.listdir(path) if f.lower().endswith('.jpg')]):
            fpath = os.path.join(path, f)
            x = ImageLoader(fpath, n)
            x.shout.image_loaded.connect(self.update_image)
            list_widget.addItem(QtGui.QListWidgetItem(QtGui.QIcon(tempimg), f))
            tpool.start(x)

    def update_image(self, img, row):
        pm = QtGui.QPixmap.fromImage(img)
        item = self.img_list.item(row)
        item.setIcon(QtGui.QIcon(pm))


class ImageLoader(QtCore.QRunnable):
    class ShoutMan(QtCore.QObject):
        image_loaded = QtCore.pyqtSignal(QtGui.QImage, int)
    def __init__(self, path, row):
        super().__init__()
        self.path = path
        self.row = row
        self.shout = self.ShoutMan()

    def run(self):
        img = QtGui.QImage(self.path)
        if img.isNull():
            print(self.path, 'wasnt\'t loaded')
        else:
            img = img.scaled(100*2, 100*2, QtCore.Qt.KeepAspectRatio)
            img = img.scaled(img.width()/2, img.height()/2,
                            QtCore.Qt.IgnoreAspectRatio,
                            QtCore.Qt.SmoothTransformation)
            self.shout.image_loaded.emit(img, self.row)


def main():
    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    app.setActiveWindow(window)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
