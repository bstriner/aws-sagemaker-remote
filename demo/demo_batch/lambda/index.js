// Command-line flags are passed to the Lambda as environment variables
const myCustomFlag = process.env.MY_CUSTOM_FLAG

// Handler receives list of tasks and returns a result for each one
async function handler(event) {
    let results = await Promise.all(event.tasks.map(
        async ({
            taskId,
            s3Key,
            s3BucketArn
        }) => {
            let bucket = s3BucketArn.split(":").pop()
            let path = `s3://${bucket}/${s3Key}`
            // do something with the file
            return {
                taskId: taskId,
                resultCode: "Succeeded",
                resultString: "Arbitrary result string for report"
            }
        }
    ))
    return {
        invocationSchemaVersion: "1.0",
        treatMissingKeysAs: "PermanentFailure",
        invocationId: event.invocationId,
        results: results
    }
}

// Export the handler
export { handler }