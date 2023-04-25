const AWS = require("aws-sdk");
const ses = new AWS.SES()


module.exports.createContact = async (event,context) => {

  console.log("EVENT:::" + event);

  // Get details from form needed for email
  const {to, from, subject, message} = JSON.parse(event.body);

  // Check if properties have been set correctly
  if(!to || !from || !subject || !message){
    const response = {
      headers: {
        "Content-Type": "application/json",
        "Access-Control-Allow-Methods": "*",
        "Access-Control-Allow-Origin": "*",
      },
      statusCode: 400,
      body: JSON.stringify({message: "One of the properties are not set correctly"})
    };
    return response
  }
  
  const emailParams = {
    Destination: {
      ToAddresses: [to],
    },
    Message: {
      Subject: { Data:subject},
      Body: {
        Text: { Data: message}
      },
    },
    Source: from
  }

  try{
    // await as async fn
    await ses.sendEmail(emailParams).promise();
    return {
      statusCode: 200,
      headers: {
        "Content-Type": "application/json",
        "Access-Control-Allow-Methods": "*",
        "Access-Control-Allow-Origin": "*",
      },
      body: JSON.stringify({message: "Email has been sent successfully.",
        success: true})
    }

  } catch (error){
      console.error(error);
      return {
        statusCode: 400,
        headers: {
          "Content-Type": "application/json",
          "Access-Control-Allow-Methods": "*",
          "Access-Control-Allow-Origin": "*",
        },
        body: JSON.stringify({message: "Email failed to send.",
        success: false}) 
      }
  }
};
