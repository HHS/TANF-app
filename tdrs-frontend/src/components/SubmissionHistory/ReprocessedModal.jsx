import Modal from '../Modal'

const Message = ({ date }) => {
  return (
    <>
      We've reprocessed your submission with updated validation criteria, based
      on system improvements, to improve accuracy of error reports. No changes
      have been made to your original data submission.
      <br />
      <br />
      Data was reprocessed on: {date}
    </>
  )
}

export const ReprocessedButton = ({ date, reprocessedState }) => {
  return (
    <div>
      <button
        className="reprocessed"
        onClick={() => {
          reprocessedState.setDate(date)
          reprocessedState.setModalVisible(true)
        }}
      >
        Reprocessed &#9432;
      </button>
    </div>
  )
}

const ReprocessedModal = ({ date, isVisible, setModalVisible }) => {
  const message = <Message date={date} />
  return (
    <Modal
      title="Most Recent Reprocessed Date"
      message={message}
      isVisible={isVisible}
      buttons={[
        {
          key: '1',
          text: 'Close',
          onClick: () => {
            setModalVisible(false)
          },
        },
      ]}
    />
  )
}

export default ReprocessedModal
