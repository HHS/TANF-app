import React, { useState } from 'react'
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

const ReprocessedModal = ({ date }) => {
  const [modalVisible, setModalVisible] = useState(false)
  const message = <Message date={date} />
  return (
    <div>
      <br />
      <button className="reprocessed" onClick={() => setModalVisible(true)}>
        Reprocessed &#9432;
      </button>
      <br />
      <br />
      <Modal
        title="Most Recent Reprocessed Date"
        message={message}
        isVisible={modalVisible}
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
    </div>
  )
}

export default ReprocessedModal
