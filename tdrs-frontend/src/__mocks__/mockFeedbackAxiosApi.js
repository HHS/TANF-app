/**
 * mockFeedbackAxiosApi.js
 *
 * Using this stub (mock) api call for UI development should be replaced with real api call
 * once it is created in follow up ticket.
 */
export const feedbackPost = async (url, data) => {
  console.log(`[FAKE API] POST to ${url} with`, data)

  // Simulate delay
  await new Promise((resolve) => setTimeout(resolve, 400))

  // Simulate success or failure based on input
  if (data.rating !== undefined) {
    return {
      data: { message: 'Fake success response from dev stub' },
      status: 200,
    }
  } else {
    const error = {
      response: {
        status: 400,
        data: { message: 'Error: Rating is required for feedback submission' },
      },
    }
    throw error
  }
}
