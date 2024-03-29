const AWS = require('aws-sdk')

const TODO_TABLE = process.env.TODO_TABLE;
const dynamoDb = new AWS.DynamoDB.DocumentClient();

module.exports.deleteTodo = (event,context,callback) => {
    const params = {
        TableName:TODO_TABLE,
        Key : {
            userId : event.pathParameters.id,
        },
    };

    dynamoDb.delete(params,(error,data) => {
        if (error) {
            console.error(error);
            callback( new Error(error));
            return;
        }

        const response = data.Item
        ? {
            statusCode : 200,
            body : JSON.stringify(data.Item)

        }
        : {
            statusCode: 400,
            body : JSON.stringify({message: "No Id for that Todo found. Nothing deleted."}),
        };
        callback(null,response);
    });
}