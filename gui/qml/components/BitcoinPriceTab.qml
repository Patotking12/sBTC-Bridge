import QtQuick 2.12
import QtQuick.Controls 2.12
import QtQuick.Layouts 1.12

Item {
    id: root

    property alias priceLabel: priceLabel
    property alias refreshButton: refreshButton

    ColumnLayout {
        anchors.fill: parent

        Label {
            id: priceLabel
            text: qsTr("Current Bitcoin price (USD):")
            font.bold: true
            Layout.alignment: Qt.AlignHCenter
        }

        Button {
            id: refreshButton
            text: qsTr("Refresh")
            Layout.alignment: Qt.AlignHCenter
        }
    }
}
