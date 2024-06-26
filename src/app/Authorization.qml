import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Window
import QtQuick.Controls.Universal

// Окно авторизации
ApplicationWindow {
    id: authorization
    width: 600
    height: 400
    title: "Authorization"
    color: "#D9D9D9"
    flags: Qt.Window | Qt.MSWindowsFixedSizeDialogHint | Qt.WindowTitleHint | Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint
    visible: true

    // Сетка окна
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 12
        spacing: 24

        // Верхний текст окна
        Text {
            id: welcome
            horizontalAlignment: Qt.AlignHCenter
            text: "В HUB тебе понадобится только\nимя."
            font.weight: Font.Bold
            font.family: "Inter"
            font.pixelSize: 32
            Layout.alignment: Qt.AlignHCenter
        }

        // Прямоугольник нижней части авторизации
        Item {
            Layout.preferredWidth: 552
            Layout.preferredHeight: 236
            Layout.alignment: Qt.AlignHCenter

            ColumnLayout {
                spacing: 12
                anchors.fill: parent
                anchors.topMargin: 24
                anchors.bottomMargin: 24

                Text {
                    Layout.bottomMargin: 2
                    text: "Укажите ваше имя, по которому пользователи\nHUB могут вас определить."
                    font.family: "Inter"
                    font.pixelSize: 16
                }

                // Строка ввода имени
                Rectangle {
                    Layout.preferredWidth: 291
                    Layout.preferredHeight: 27
                    border.width: 1
                    clip: true
                    TextInput {
                        id: input
                        anchors.fill: parent
                        anchors.margins: 4
                        font.pixelSize: 16
                        color: "black"
                        property string placeholderText: "Введите ваше имя..."
                        Text {
                            text: parent.placeholderText
                            font.family: "Inter"
                            font.pixelSize: parent.font.pixelSize
                            color: "#aaa"
                            visible: !parent.text
                        }
                    }
                }

                Button {
                    id: login
                    Layout.preferredWidth: 140
                    Layout.preferredHeight: 42
                    background: Rectangle {
                        border.width: 1
                    }
                    text: "Войти"
                    font.family: "Inter"
                    font.pixelSize: 20

                    onClicked: {
                        authorization.close()
                        main_control.main_window(input.text)
                    }
                }

                Item {
                    Layout.preferredWidth: 100
                    Layout.preferredHeight: 100
                }
            }
        }

        RowLayout {
            Layout.preferredWidth: 56
            Layout.preferredHeight: 14
            Layout.alignment: Qt.AlignHCenter

            Image {
                source: "icons/HUB 2024.svg"
            }

            Image {
                source: "icons/©.svg"
            }
        }
    }

    Item {
        id: authors
        width: 1348
        height: 77
        rotation: -49
        x: 167
        y: -160
        Text {
            anchors.verticalCenter: parent.verticalCenter
            anchors.left: parent.left
            horizontalAlignment: Qt.AlignHCenter
            text: "S/B.I.A/M.N.N/K.I.R/L.A.V/P.M.Y/B.D.A/P.M.S/B.I.A/M.N.N"
            font.weight: Font.Bold
            font.family: "Inter"
            font.pixelSize: 64
            PathAnimation {
                target: authors
                path: Path {
                    startX: 127; startY: -120
                    PathLine {x: -842; y: 995}
                }
                running: true
                duration: 5500
                loops: Animation.Infinite
            }
        }
    }
}
