var source = new EventSource("https://webhook.app.crdlpt.com/stream");
source.onmessage = function(event) {
  var table = $("#table-data");
  var data = JSON.parse(event.data);
  var id = data._id
  var time = data.detected_at
  var type = data.type
  var message = data.message
  var row = $("<tr>");
  var cell1 = $("<td>").text(id);
  var cell2 = $("<td>").text(time);
  var cell3 = $("<td>").text(type);
  var cell4 = $("<td>").text(message);
  row.append(cell1, cell2, cell3, cell4);
  table.append(row);
};