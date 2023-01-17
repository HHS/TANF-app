import React from 'react'
import PropTypes from 'prop-types'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import {
  faChevronLeft,
  faChevronRight,
} from '@fortawesome/free-solid-svg-icons'

const PaginatorArrowButton = ({ label, arrowDirection, onClick }) => (
  <li className="usa-pagination__item usa-pagination__arrow">
    <button
      onClick={onClick}
      className="usa-pagination__link usa-pagination__previous-page"
      aria-label="Previous page"
    >
      {arrowDirection === 'left' ? (
        <svg className="usa-icon" aria-hidden="true" role="img">
          <FontAwesomeIcon className="margin-right-1" icon={faChevronLeft} />
        </svg>
      ) : null}

      <span className="usa-pagination__link-text">{label}</span>

      {arrowDirection === 'right' ? (
        <svg className="usa-icon" aria-hidden="true" role="img">
          <FontAwesomeIcon className="margin-left-1" icon={faChevronRight} />
        </svg>
      ) : null}
    </button>
  </li>
)

PaginatorArrowButton.propTypes = {
  label: PropTypes.string,
  arrowDirection: PropTypes.oneOf(['left', 'right']),
  onClick: PropTypes.func,
}

const PaginatorPageNumberButton = ({ label, isSelected, onClick }) => (
  <li className="usa-pagination__item usa-pagination__page-no">
    <button
      onClick={onClick}
      className={
        isSelected
          ? 'usa-pagination__button usa-current'
          : 'usa-pagination__button'
      }
      aria-label={`Page ${label}`}
      aria-current="page"
    >
      {label}
    </button>
  </li>
)

PaginatorPageNumberButton.propTypes = {
  label: PropTypes.string,
  isSelected: PropTypes.bool,
  onClick: PropTypes.func,
}

const Paginator = ({ pages, selected, onChange }) => (
  <nav aria-label="Pagination" className="usa-pagination">
    <ul className="usa-pagination__list">
      <PaginatorArrowButton
        label="Previous"
        arrowDirection="left"
        onClick={() => onChange(selected - 1)}
      />

      {Array(pages)
        .keys()
        .map((i) => {
          ;<PaginatorPageNumberButton
            label="1"
            isSelected={selected === 1}
            onClick={() => onChange(1)}
          />
        })}

      <PaginatorArrowButton
        label="Next"
        arrowDirection="right"
        onClick={() => onChange(selected + 1)}
      />
    </ul>
  </nav>
)

Paginator.propTypes = {
  pages: PropTypes.number,
  selected: PropTypes.number,
  onChange: PropTypes.func,
}

export default Paginator
