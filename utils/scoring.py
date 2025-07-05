import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any
import streamlit as st

class PropertyScorer:
    """Handles property scoring and ranking algorithms"""
    
    def __init__(self):
        # Default scoring weights
        self.default_weights = {
            'roi': 0.25,
            'cap_rate': 0.20,
            'cash_flow': 0.20,
            'dscr': 0.15,
            'location': 0.10,
            'condition': 0.10
        }
        
        # Market benchmarks for normalization
        self.benchmarks = {
            'roi': {'excellent': 15, 'good': 10, 'average': 8, 'poor': 5},
            'cap_rate': {'excellent': 8, 'good': 6, 'average': 5, 'poor': 3},
            'cash_flow': {'excellent': 1000, 'good': 500, 'average': 200, 'poor': 0},
            'dscr': {'excellent': 1.5, 'good': 1.25, 'average': 1.1, 'poor': 1.0}
        }
    
    def calculate_individual_scores(self, property_data: Dict, calculator) -> Dict:
        """Calculate individual component scores for a property"""
        try:
            # Calculate financial metrics
            metrics = calculator.calculate_comprehensive_metrics(property_data)
            
            scores = {}
            
            # ROI Score (0-100)
            roi = metrics.get('roi', 0)
            scores['roi_score'] = self._normalize_score(roi, 'roi')
            
            # Cap Rate Score (0-100)
            cap_rate = metrics.get('cap_rate', 0)
            scores['cap_rate_score'] = self._normalize_score(cap_rate, 'cap_rate')
            
            # Cash Flow Score (0-100)
            cash_flow = metrics.get('monthly_cash_flow', 0)
            scores['cash_flow_score'] = self._normalize_score(cash_flow, 'cash_flow')
            
            # DSCR Score (0-100)
            dscr = metrics.get('dscr', 0)
            scores['dscr_score'] = self._normalize_score(dscr, 'dscr')
            
            # Location Score (subjective, based on available data)
            scores['location_score'] = self._calculate_location_score(property_data)
            
            # Condition Score (subjective, based on available data)
            scores['condition_score'] = self._calculate_condition_score(property_data)
            
            return scores
            
        except Exception as e:
            st.error(f"Error calculating individual scores: {str(e)}")
            return {}
    
    def _normalize_score(self, value: float, metric_type: str) -> float:
        """Normalize a metric value to a 0-100 score"""
        try:
            if metric_type not in self.benchmarks:
                return 50  # Default neutral score
            
            benchmark = self.benchmarks[metric_type]
            
            if value >= benchmark['excellent']:
                return 100
            elif value >= benchmark['good']:
                # Linear interpolation between good and excellent
                return 80 + (20 * (value - benchmark['good']) / (benchmark['excellent'] - benchmark['good']))
            elif value >= benchmark['average']:
                # Linear interpolation between average and good
                return 60 + (20 * (value - benchmark['average']) / (benchmark['good'] - benchmark['average']))
            elif value >= benchmark['poor']:
                # Linear interpolation between poor and average
                return 40 + (20 * (value - benchmark['poor']) / (benchmark['average'] - benchmark['poor']))
            else:
                # Below poor threshold
                return max(0, 40 * (value / benchmark['poor']))
                
        except Exception as e:
            st.error(f"Error normalizing score for {metric_type}: {str(e)}")
            return 50
    
    def _calculate_location_score(self, property_data: Dict) -> float:
        """Calculate location score based on available data"""
        try:
            score = 50  # Start with neutral score
            
            # Adjust based on neighborhood (if available)
            neighborhood = property_data.get('neighborhood', '').lower()
            
            # Simple heuristic based on common neighborhood indicators
            good_indicators = ['downtown', 'center', 'historic', 'waterfront', 'hills']
            poor_indicators = ['industrial', 'highway', 'remote', 'flood']
            
            for indicator in good_indicators:
                if indicator in neighborhood:
                    score += 10
            
            for indicator in poor_indicators:
                if indicator in neighborhood:
                    score -= 10
            
            # School district bonus
            if property_data.get('school_district'):
                score += 5
            
            return max(0, min(100, score))
            
        except Exception as e:
            st.error(f"Error calculating location score: {str(e)}")
            return 50
    
    def _calculate_condition_score(self, property_data: Dict) -> float:
        """Calculate condition score based on available data"""
        try:
            score = 50  # Start with neutral score
            
            # Age of property
            year_built = property_data.get('year_built', 2000)
            current_year = 2024
            age = current_year - year_built
            
            if age < 5:
                score += 20  # New construction
            elif age < 15:
                score += 10  # Relatively new
            elif age < 30:
                score += 0   # Average age
            elif age < 50:
                score -= 10  # Older property
            else:
                score -= 20  # Very old property
            
            # Size factor (larger properties often better maintained)
            square_feet = property_data.get('square_feet', 0)
            if square_feet > 2500:
                score += 5
            elif square_feet < 1000:
                score -= 5
            
            return max(0, min(100, score))
            
        except Exception as e:
            st.error(f"Error calculating condition score: {str(e)}")
            return 50
    
    def calculate_composite_score(self, property_data: Dict, calculator, weights: Dict = None) -> Dict:
        """Calculate composite score for a property"""
        try:
            if weights is None:
                weights = self.default_weights
            
            # Get individual scores
            individual_scores = self.calculate_individual_scores(property_data, calculator)
            
            if not individual_scores:
                return {'composite_score': 0, 'individual_scores': {}}
            
            # Calculate weighted composite score
            composite_score = 0
            total_weight = 0
            
            score_mapping = {
                'roi': 'roi_score',
                'cap_rate': 'cap_rate_score',
                'cash_flow': 'cash_flow_score',
                'dscr': 'dscr_score',
                'location': 'location_score',
                'condition': 'condition_score'
            }
            
            for weight_key, weight_value in weights.items():
                if weight_key in score_mapping:
                    score_key = score_mapping[weight_key]
                    if score_key in individual_scores:
                        composite_score += individual_scores[score_key] * weight_value
                        total_weight += weight_value
            
            # Normalize if total weight is not 1
            if total_weight > 0:
                composite_score = composite_score / total_weight
            
            return {
                'composite_score': composite_score,
                'individual_scores': individual_scores,
                'weights_used': weights
            }
            
        except Exception as e:
            st.error(f"Error calculating composite score: {str(e)}")
            return {'composite_score': 0, 'individual_scores': {}}
    
    def rank_properties(self, properties_df: pd.DataFrame, calculator, weights: Dict = None) -> pd.DataFrame:
        """Rank all properties based on composite scores"""
        try:
            if properties_df.empty:
                return pd.DataFrame()
            
            if weights is None:
                weights = self.default_weights
            
            ranked_properties = []
            
            for _, property_data in properties_df.iterrows():
                scoring_result = self.calculate_composite_score(property_data, calculator, weights)
                
                property_ranking = {
                    'address': property_data['address'],
                    'property_type': property_data['property_type'],
                    'price': property_data['price'],
                    'monthly_rent': property_data['monthly_rent'],
                    'composite_score': scoring_result['composite_score'],
                    'roi_score': scoring_result['individual_scores'].get('roi_score', 0),
                    'cap_rate_score': scoring_result['individual_scores'].get('cap_rate_score', 0),
                    'cash_flow_score': scoring_result['individual_scores'].get('cash_flow_score', 0),
                    'dscr_score': scoring_result['individual_scores'].get('dscr_score', 0),
                    'location_score': scoring_result['individual_scores'].get('location_score', 0),
                    'condition_score': scoring_result['individual_scores'].get('condition_score', 0)
                }
                
                ranked_properties.append(property_ranking)
            
            # Convert to DataFrame and sort by composite score
            ranked_df = pd.DataFrame(ranked_properties)
            ranked_df = ranked_df.sort_values('composite_score', ascending=False)
            ranked_df['rank'] = range(1, len(ranked_df) + 1)
            
            return ranked_df
            
        except Exception as e:
            st.error(f"Error ranking properties: {str(e)}")
            return pd.DataFrame()
    
    def get_investment_recommendations(self, properties_df: pd.DataFrame, calculator, top_n: int = 5) -> List[Dict]:
        """Get investment recommendations based on scoring"""
        try:
            ranked_df = self.rank_properties(properties_df, calculator)
            
            if ranked_df.empty:
                return []
            
            recommendations = []
            
            # Get top N properties
            top_properties = ranked_df.head(top_n)
            
            for _, prop in top_properties.iterrows():
                # Generate recommendation reasoning
                reasoning = self._generate_recommendation_reasoning(prop)
                
                recommendation = {
                    'address': prop['address'],
                    'rank': prop['rank'],
                    'composite_score': prop['composite_score'],
                    'price': prop['price'],
                    'monthly_rent': prop['monthly_rent'],
                    'reasoning': reasoning,
                    'strengths': self._identify_strengths(prop),
                    'weaknesses': self._identify_weaknesses(prop),
                    'risk_level': self._assess_risk_level(prop)
                }
                
                recommendations.append(recommendation)
            
            return recommendations
            
        except Exception as e:
            st.error(f"Error generating recommendations: {str(e)}")
            return []
    
    def _generate_recommendation_reasoning(self, property_data: Dict) -> str:
        """Generate reasoning for property recommendation"""
        try:
            score = property_data['composite_score']
            
            if score >= 80:
                return "Excellent investment opportunity with strong metrics across all categories."
            elif score >= 70:
                return "Very good investment with solid performance in most key areas."
            elif score >= 60:
                return "Good investment opportunity with moderate returns and acceptable risk."
            elif score >= 50:
                return "Fair investment with some positive aspects but also areas of concern."
            else:
                return "Below-average investment opportunity with significant risks or low returns."
                
        except Exception as e:
            st.error(f"Error generating recommendation reasoning: {str(e)}")
            return "Unable to generate reasoning."
    
    def _identify_strengths(self, property_data: Dict) -> List[str]:
        """Identify property strengths based on scores"""
        try:
            strengths = []
            
            score_categories = {
                'roi_score': 'Strong ROI potential',
                'cap_rate_score': 'Attractive capitalization rate',
                'cash_flow_score': 'Positive cash flow generation',
                'dscr_score': 'Excellent debt coverage',
                'location_score': 'Prime location',
                'condition_score': 'Good property condition'
            }
            
            for score_key, description in score_categories.items():
                if score_key in property_data and property_data[score_key] >= 70:
                    strengths.append(description)
            
            return strengths
            
        except Exception as e:
            st.error(f"Error identifying strengths: {str(e)}")
            return []
    
    def _identify_weaknesses(self, property_data: Dict) -> List[str]:
        """Identify property weaknesses based on scores"""
        try:
            weaknesses = []
            
            score_categories = {
                'roi_score': 'Low ROI potential',
                'cap_rate_score': 'Poor capitalization rate',
                'cash_flow_score': 'Negative or low cash flow',
                'dscr_score': 'Inadequate debt coverage',
                'location_score': 'Suboptimal location',
                'condition_score': 'Poor property condition'
            }
            
            for score_key, description in score_categories.items():
                if score_key in property_data and property_data[score_key] <= 40:
                    weaknesses.append(description)
            
            return weaknesses
            
        except Exception as e:
            st.error(f"Error identifying weaknesses: {str(e)}")
            return []
    
    def _assess_risk_level(self, property_data: Dict) -> str:
        """Assess risk level based on property scores"""
        try:
            # Risk factors
            risk_score = 0
            
            # DSCR is most important for risk
            dscr_score = property_data.get('dscr_score', 50)
            if dscr_score < 40:
                risk_score += 30
            elif dscr_score < 60:
                risk_score += 15
            
            # Cash flow risk
            cash_flow_score = property_data.get('cash_flow_score', 50)
            if cash_flow_score < 40:
                risk_score += 25
            elif cash_flow_score < 60:
                risk_score += 10
            
            # Location risk
            location_score = property_data.get('location_score', 50)
            if location_score < 40:
                risk_score += 15
            elif location_score < 60:
                risk_score += 5
            
            # Condition risk
            condition_score = property_data.get('condition_score', 50)
            if condition_score < 40:
                risk_score += 10
            
            # Determine risk level
            if risk_score >= 50:
                return "High Risk"
            elif risk_score >= 25:
                return "Medium Risk"
            else:
                return "Low Risk"
                
        except Exception as e:
            st.error(f"Error assessing risk level: {str(e)}")
            return "Unknown Risk"
    
    def compare_properties(self, properties_df: pd.DataFrame, calculator, property_addresses: List[str]) -> Dict:
        """Compare specific properties side by side"""
        try:
            if not property_addresses:
                return {}
            
            # Filter properties
            filtered_df = properties_df[properties_df['address'].isin(property_addresses)]
            
            if filtered_df.empty:
                return {}
            
            comparison_results = {}
            
            for _, prop in filtered_df.iterrows():
                scoring_result = self.calculate_composite_score(prop, calculator)
                
                comparison_results[prop['address']] = {
                    'composite_score': scoring_result['composite_score'],
                    'individual_scores': scoring_result['individual_scores'],
                    'property_data': {
                        'price': prop['price'],
                        'monthly_rent': prop['monthly_rent'],
                        'property_type': prop['property_type'],
                        'bedrooms': prop['bedrooms'],
                        'bathrooms': prop['bathrooms'],
                        'square_feet': prop['square_feet']
                    }
                }
            
            return comparison_results
            
        except Exception as e:
            st.error(f"Error comparing properties: {str(e)}")
            return {}
    
    def get_scoring_explanation(self) -> Dict:
        """Get explanation of the scoring methodology"""
        return {
            'methodology': {
                'description': 'Properties are scored on a 0-100 scale across multiple categories',
                'categories': {
                    'ROI': 'Return on Investment - measures profitability',
                    'Cap Rate': 'Capitalization Rate - measures property yield',
                    'Cash Flow': 'Monthly cash flow generation',
                    'DSCR': 'Debt Service Coverage Ratio - measures debt safety',
                    'Location': 'Location quality assessment',
                    'Condition': 'Property condition and age factors'
                },
                'weights': self.default_weights,
                'benchmarks': self.benchmarks
            },
            'score_ranges': {
                '90-100': 'Exceptional investment opportunity',
                '80-89': 'Excellent investment',
                '70-79': 'Very good investment',
                '60-69': 'Good investment',
                '50-59': 'Fair investment',
                '40-49': 'Below average investment',
                '0-39': 'Poor investment opportunity'
            }
        }
    
    def update_benchmarks(self, new_benchmarks: Dict):
        """Update scoring benchmarks"""
        try:
            self.benchmarks.update(new_benchmarks)
            return True
        except Exception as e:
            st.error(f"Error updating benchmarks: {str(e)}")
            return False
    
    def update_weights(self, new_weights: Dict):
        """Update default scoring weights"""
        try:
            # Validate weights sum to 1
            total_weight = sum(new_weights.values())
            if abs(total_weight - 1.0) > 0.01:
                st.warning(f"Weights sum to {total_weight:.2f}, normalizing to 1.0")
                new_weights = {k: v/total_weight for k, v in new_weights.items()}
            
            self.default_weights.update(new_weights)
            return True
        except Exception as e:
            st.error(f"Error updating weights: {str(e)}")
            return False
