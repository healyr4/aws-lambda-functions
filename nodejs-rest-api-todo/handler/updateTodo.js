const AWS = require('aws-sdk')

const TODO_TABLE = process.env.TODO_TABLE;
const dynamoDb = new AWS.DynamoDB.DocumentClient();

module.exports.updateTodo = (event, context, callback) => {

    const dateTime = new Date().toISOString;
    const data = JSON.parse(event.body)

    if (typeof data.todo !== "string" || typeof data.checked !== "boolean"){
        console.error("The value of todo or checked in the JSON is not valid");
        return;
    }

    const params = {
        TableName : TODO_TABLE,
        Key : {
            userId : event.pathParameters.id,
        },
        ExpressionAttributeNames:{
            "#todo_json" : "todo",
        },
        ExpressionAttributeValues:{
            ":todo": data.todo,
            ":checked": data.checked,
            ":updatedAt": dateTime,
        },
        UpdateExpression:
        // Script to be read in AWS.DynamoDB
            "SET #todo_json = :todo, checked = :checked, updatedAt = :updatedAt",
        ReturnValues: "ALL_NEW" 
    };

    dynamoDb.update(params,(error,data) => {
    if (error) {
        console.error(error);
        callback (new Error(error));
        return;
    }

    const response = {
        statusCode: 200,
        body: JSON.stringify(data.Attributes)
    };
    callback(null, response);
    });   
};