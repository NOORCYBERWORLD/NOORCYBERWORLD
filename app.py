function doPost(e) {
  try {
    var ss = SpreadsheetApp.openById("1kFmyKMRLT8VA9Fq2yuKnZcJGy7KCiT65c7dG0zMeY68");
    var sheet = ss.getSheets()[0];
    
    var data = {};
    if (e && e.parameter && Object.keys(e.parameter).length > 0) {
      data = e.parameter;
    } else if (e && e.postData && e.postData.contents) {
      data = JSON.parse(e.postData.contents);
    }
    
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
      .createTextOutput(JSON.stringify({ "status": "success" }))
      .setMimeType(ContentService.MimeType.JSON);
      
  } catch (err) {
    return ContentService
      .createTextOutput(JSON.stringify({ "status": "error", "error": err.toString() }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}
