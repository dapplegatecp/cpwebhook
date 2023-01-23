var source = new EventSource("https://webhook.app.crdlpt.com/stream");
source.onmessage = function(event) {
  var table = $("#table-data");
  var data = JSON.parse(event.data);
  var row = $("<tr>");
  var cells = [
    $("<td>").text(data._id),
    $("<td>").text(data.detected_at),
    $("<td>").text(data.type),
    $("<td>").text(data.friendly_info),
    $("<td>").text(data.router),
    $("<td>").text(data.router_name),
    $("<td>").text(data.router_description),
    $("<td>").text(data.router_mac),
    $("<td>").text(data.router_serial_number),
    $("<td>").text(data.router_asset_id),
    $("<td>").text(data.router_custom1),
    $("<td>").text(data.router_custom2),
  ]
  row.append(cells);
  table.append(row);
};