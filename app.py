function doGet(e) {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  var data = sheet.getDataRange().getValues();
  var result = [];
  
  if (data.length > 1) {
    for (var i = 1; i < data.length; i++) {
      var row = data[i];
      if (row[0] !== "" || row[1] !== "") {
        result.push({
          "created_at": formatDate(row[0]),
          "name": String(row[1] || ""),
          "mobile": String(row[2] || ""),
          "service": String(row[3] || ""),
          "amount": Number(row[4] || 0),       // Gross Amount
          "net_amount": Number(row[5] || 0),   // Net Income
          "payment": String(row[6] || ""),
          "expiry": String(row[7] || "N/A"),
          "_row_number": i + 1
        });
      }
    }
  }
  
  return ContentService.createTextOutput(JSON.stringify(result))
    .setMimeType(ContentService.MimeType.JSON);
}

function doPost(e) {
  try {
    var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
    var params = {};
    
    if (e.postData && e.postData.contents) {
      try {
        params = JSON.parse(e.postData.contents);
      } catch(err) {
        params = e.parameter;
      }
    } else {
      params = e.parameter;
    }

    var action = params.action;

    if (action === "add") {
      sheet.appendRow([
        params.created_at,
        params.name,
        params.mobile,
        params.service,
        params.amount,
        params.net_amount,
        params.payment,
        params.expiry
      ]);
      return responseJSON({ success: true, message: "Entry added successfully" });
    } 
    
    else if (action === "edit") {
      var rowNum = parseInt(params.row_number);
      if (rowNum && rowNum > 1) {
        sheet.getRange(rowNum, 1, 1, 8).setValues([[
          params.created_at,
          params.name,
          params.mobile,
          params.service,
          params.amount,
          params.net_amount,
          params.payment,
          params.expiry
        ]]);
        return responseJSON({ success: true, message: "Entry updated successfully" });
      }
    } 
    
    else if (action === "delete") {
      var rowNum = parseInt(params.row_number);
      if (rowNum && rowNum > 1) {
        sheet.deleteRow(rowNum);
        return responseJSON({ success: true, message: "Entry deleted successfully" });
      }
    }

    return responseJSON({ success: false, message: "Invalid Action or Row Number" });

  } catch (error) {
    return responseJSON({ success: false, error: error.toString() });
  }
}

function formatDate(dateVal) {
  if (!dateVal) return "";
  if (dateVal instanceof Date) {
    var yyyy = dateVal.getFullYear();
    var mm = String(dateVal.getMonth() + 1).padStart(2, '0');
    var dd = String(dateVal.getDate()).padStart(2, '0');
    return yyyy + "-" + mm + "-" + dd;
  }
  return String(dateVal);
}

function responseJSON(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}
