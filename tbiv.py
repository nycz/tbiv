import os
import os.path
import sys

from PyQt4 import QtGui, QtCore


class MainWindow(QtGui.QFrame):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('TBIV')
        self.thumb_size = (100, 100)
        self.ok_exts = ('.jpg', '.png')

        layout = QtGui.QHBoxLayout(self)
        lw = QtGui.QListWidget
        self.img_list = lw()
        self.img_list.setViewMode(lw.IconMode)
        self.img_list.setMovement(lw.Static)
        self.img_list.setUniformItemSizes(True)
        self.img_list.setBatchSize(10)
        self.img_list.setLayoutMode(lw.Batched)
        self.img_list.setSelectionMode(lw.ExtendedSelection)
        self.img_list.setIconSize(QtCore.QSize(*self.thumb_size))
        self.img_list.setResizeMode(lw.Adjust)
        path = r'.'
        self.show_directory(self.img_list, path)
        layout.addWidget(self.img_list)
        self.show()
        self.resize(1024,768)

        QtGui.QShortcut(QtGui.QKeySequence("Ctrl+O"), self, self.open_directory)

    def open_directory(self):
        dialog = QtGui.QFileDialog()
        dialog.setFileMode(QtGui.QFileDialog.Directory)
        dialog.setOption(QtGui.QFileDialog.ShowDirsOnly)
        if dialog.exec_():
            self.show_directory(self.img_list, dialog.selectedFiles()[0])

    def show_directory(self, list_widget, path):
        list_widget.clear()
        tpool = QtCore.QThreadPool.globalInstance()
        tempimg = QtGui.QPixmap(*self.thumb_size)
        tempimg.fill()
        for n,f in enumerate([f for f in os.listdir(path) if f[-4:] in self.ok_exts]):
            fpath = os.path.join(path, f)
            x = ImageLoader(fpath, n, self.thumb_size)
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
    def __init__(self, path, row, thumb_size):
        super().__init__()
        self.path = path
        self.row = row
        self.w, self.h = thumb_size
        self.shout = self.ShoutMan()

    def run(self):
        img = QtGui.QImage(self.path)
        if img.isNull():
            print(self.path, 'wasnt\'t loaded')
        else:
            img = img.scaled(self.w*2, self.h*2, QtCore.Qt.KeepAspectRatio)
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
