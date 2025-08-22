// utils/regions.js

export const regionNames = [
  'Boston',
  'New York',
  'Philadelphia',
  'Atlanta',
  'Chicago',
  'Dallas',
  'Kansas City',
  'Denver',
  'San Francisco',
  'Seattle',
]

/**
 * Get the region name by its numeric ID (1–10)
 * @param {number} id - Region number (1–10)
 * @returns {string} Region name, or "Unknown" if out of bounds
 */
export const getRegionNameById = (id) => {
  if (id >= 1 && id <= regionNames.length) {
    return regionNames[id - 1]
  }
  return 'Unknown'
}

export const addRegion = (regionsSet, id, name) => {
  const newSet = new Set(regionsSet)
  newSet.add({ id, name })
  return newSet
}

export const removeRegionById = (regionsSet, id) => {
  return new Set(Array.from(regionsSet).filter((r) => r.id !== id))
}
