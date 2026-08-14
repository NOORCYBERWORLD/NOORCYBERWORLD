function doPost(e) {
  try {
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var sheet = ss.getSheets()[0]; // पहली शीट को ऑटो-सेलेक्ट करेगा
    
    var data;
    if (e.postData && e.postData.contents) {
      data = JSON.parse(e.postData.contents);
    } else {
      data = e.parameter;
    }
    
    // डेटा को Sheet की अगली Row में जोड़ना
    sheet.appendRow([
      data.created_at || "",
      data.name || "",
      data.mobile || "",
      data.service || "",
      data.amount || 0,
      data.payment || "",
      data.expiry || ""
    ]);
    
    return ContentService
      .createTextOutput(JSON.stringify({ "status": "success", "message": "Row added successfully" }))
      .setMimeType(ContentService.MimeType.JSON);
      
  } catch (err) {
    return ContentService
      .createTextOutput(JSON.stringify({ "status": "error", "message": err.toString() }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

function doGet(e) {
  try {
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var sheet = ss.getSheets()[0];
    var rows = sheet.getDataRange().getValues();
    
    if (rows.length <= 1) {
      return ContentService.createTextOutput(JSON.stringify([])).setMimeType(ContentService.MimeType.JSON);
    }
    
    var headers = rows[0];
    var data = [];
    
    for (var i = 1; i < rows.length; i++) {
      var row = rows[i];
      if (row.join("").trim() !== "") {
        var record = {};
        for (var j = 0; j < headers.length; j++) {
          var key = headers[j].toString().trim().toLowerCase();
          var val = row[j];
          if (val instanceof Date) {
            val = Utilities.formatDate(val, Session.getScriptTimeZone(), "yyyy-MM-dd");
          }
          record[key] = val;
        }
        data.push(record);
      }
    }
    
    return ContentService.createTextOutput(JSON.stringify(data)).setMimeType(ContentService.MimeType.JSON);
  } catch (err) {
    return ContentService.createTextOutput(JSON.stringify([])).setMimeType(ContentService.MimeType.JSON);
  }
}
