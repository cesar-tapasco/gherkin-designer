// Sample Gherkin scenarios for the Web Runner
// Based on actual test scenarios from the project
// All variables are properly defined

export const samples = [
{}
];

// Category grouping
export const categories = [
  'Basic',
  'CRUD',
  'Advanced',
  'Validation',
  'Workflows',
  'UI - Basic',
  'UI - Navigation',
  'UI - Forms',
  'UI - Grid Operations',
  'UI - Interactive',
  'UI - Validation',
  'UI - Workflows'
];

export function getSampleById(id) {
  return samples.find(s => s.id === id);
}

export function getSamplesByCategory(category) {
  return samples.filter(s => s.category === category);
}

export function getAllSamples() {
  return samples;
}

export function getCategories() {
  return [...new Set(samples.map(s => s.category))];
}
