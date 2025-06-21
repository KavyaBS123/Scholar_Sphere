import pandas as pd
import numpy as np
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from typing import Dict, Any, List, Tuple, Optional
import streamlit as st

class ScholarshipClustering:
    """Clustering functionality for scholarship data"""
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.pca = None
        self.feature_names = []
    
    def cluster_scholarships(self, 
                           scholarships_df: pd.DataFrame, 
                           method: str = 'kmeans',
                           n_clusters: Optional[int] = 5,
                           features: List[str] = None) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Cluster scholarships based on selected features
        
        Args:
            scholarships_df: DataFrame containing scholarship data
            method: Clustering method ('kmeans', 'hierarchical', 'dbscan')
            n_clusters: Number of clusters (for methods that require it)
            features: List of features to use for clustering
        
        Returns:
            Tuple of (clustered_dataframe, cluster_info)
        """
        if scholarships_df.empty:
            return None, None
        
        if features is None:
            features = ["Amount", "Category", "Demographics"]
        
        try:
            # Prepare features for clustering
            feature_matrix = self._prepare_features(scholarships_df, features)
            
            if feature_matrix is None or feature_matrix.shape[1] == 0:
                raise ValueError("No valid features for clustering")
            
            # Perform clustering
            if method == 'kmeans':
                cluster_labels, cluster_info = self._kmeans_clustering(feature_matrix, n_clusters)
            elif method == 'hierarchical':
                cluster_labels, cluster_info = self._hierarchical_clustering(feature_matrix, n_clusters)
            elif method == 'dbscan':
                cluster_labels, cluster_info = self._dbscan_clustering(feature_matrix)
            else:
                raise ValueError(f"Unsupported clustering method: {method}")
            
            # Add cluster labels to dataframe
            clustered_df = scholarships_df.copy()
            clustered_df['cluster'] = cluster_labels
            
            # Add cluster info
            cluster_info['method'] = method
            cluster_info['features_used'] = features
            cluster_info['n_scholarships'] = len(clustered_df)
            
            return clustered_df, cluster_info
            
        except Exception as e:
            st.error(f"Clustering failed: {str(e)}")
            return None, None
    
    def _prepare_features(self, df: pd.DataFrame, features: List[str]) -> np.ndarray:
        """Prepare feature matrix for clustering"""
        feature_columns = []
        
        # Amount feature
        if "Amount" in features:
            feature_columns.append(df['amount'].values.reshape(-1, 1))
        
        # GPA Requirement feature
        if "GPA Requirement" in features:
            feature_columns.append(df['gpa_requirement'].values.reshape(-1, 1))
        
        # Category feature (encoded)
        if "Category" in features:
            if 'category' not in self.label_encoders:
                self.label_encoders['category'] = LabelEncoder()
                category_encoded = self.label_encoders['category'].fit_transform(df['category'])
            else:
                category_encoded = self.label_encoders['category'].transform(df['category'])
            feature_columns.append(category_encoded.reshape(-1, 1))
        
        # Demographics feature (encoded as diversity score and specific encodings)
        if "Demographics" in features:
            # Diversity score (number of demographics)
            demo_diversity = df['target_demographics'].apply(len).values.reshape(-1, 1)
            feature_columns.append(demo_diversity)
            
            # Most common demographics as binary features
            all_demographics = set()
            for demo_list in df['target_demographics']:
                all_demographics.update(demo_list)
            
            common_demographics = sorted(list(all_demographics))[:10]  # Top 10 most common
            
            for demo in common_demographics:
                demo_binary = df['target_demographics'].apply(lambda x: 1 if demo in x else 0).values.reshape(-1, 1)
                feature_columns.append(demo_binary)
        
        # Deadline feature (days from now)
        if "Deadline" in features:
            try:
                deadline_dates = pd.to_datetime(df['deadline'])
                days_until = (deadline_dates - pd.Timestamp.now()).dt.days
                days_until = days_until.fillna(365)  # Default to 1 year if invalid
                feature_columns.append(days_until.values.reshape(-1, 1))
            except:
                # If deadline parsing fails, skip this feature
                pass
        
        if not feature_columns:
            return None
        
        # Combine all features
        feature_matrix = np.hstack(feature_columns)
        
        # Scale features
        feature_matrix = self.scaler.fit_transform(feature_matrix)
        
        return feature_matrix
    
    def _kmeans_clustering(self, feature_matrix: np.ndarray, n_clusters: int) -> Tuple[np.ndarray, Dict[str, Any]]:
        """Perform K-means clustering"""
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        cluster_labels = kmeans.fit_predict(feature_matrix)
        
        # Calculate clustering quality metrics
        silhouette_avg = silhouette_score(feature_matrix, cluster_labels)
        inertia = kmeans.inertia_
        
        cluster_info = {
            'silhouette_score': silhouette_avg,
            'inertia': inertia,
            'n_clusters': n_clusters,
            'cluster_centers': kmeans.cluster_centers_
        }
        
        return cluster_labels, cluster_info
    
    def _hierarchical_clustering(self, feature_matrix: np.ndarray, n_clusters: int) -> Tuple[np.ndarray, Dict[str, Any]]:
        """Perform hierarchical clustering"""
        hierarchical = AgglomerativeClustering(n_clusters=n_clusters)
        cluster_labels = hierarchical.fit_predict(feature_matrix)
        
        # Calculate clustering quality metrics
        silhouette_avg = silhouette_score(feature_matrix, cluster_labels)
        
        cluster_info = {
            'silhouette_score': silhouette_avg,
            'n_clusters': n_clusters,
            'linkage': 'ward'
        }
        
        return cluster_labels, cluster_info
    
    def _dbscan_clustering(self, feature_matrix: np.ndarray) -> Tuple[np.ndarray, Dict[str, Any]]:
        """Perform DBSCAN clustering"""
        # Automatically determine eps parameter
        eps = self._estimate_eps(feature_matrix)
        
        dbscan = DBSCAN(eps=eps, min_samples=max(2, len(feature_matrix) // 20))
        cluster_labels = dbscan.fit_predict(feature_matrix)
        
        # Handle noise points (labeled as -1) by assigning them to a separate cluster
        unique_labels = np.unique(cluster_labels)
        n_clusters = len(unique_labels) - (1 if -1 in unique_labels else 0)
        n_noise = list(cluster_labels).count(-1)
        
        # Calculate clustering quality metrics (only for non-noise points)
        if n_clusters > 1 and n_noise < len(cluster_labels):
            non_noise_mask = cluster_labels != -1
            if np.sum(non_noise_mask) > 1:
                silhouette_avg = silhouette_score(feature_matrix[non_noise_mask], cluster_labels[non_noise_mask])
            else:
                silhouette_avg = 0
        else:
            silhouette_avg = 0
        
        cluster_info = {
            'silhouette_score': silhouette_avg,
            'n_clusters': n_clusters,
            'n_noise_points': n_noise,
            'eps': eps
        }
        
        return cluster_labels, cluster_info
    
    def _estimate_eps(self, feature_matrix: np.ndarray) -> float:
        """Estimate eps parameter for DBSCAN"""
        from sklearn.neighbors import NearestNeighbors
        
        # Use k=4 as a rule of thumb
        k = min(4, len(feature_matrix) - 1)
        if k <= 0:
            return 0.5
        
        neighbors = NearestNeighbors(n_neighbors=k)
        neighbors_fit = neighbors.fit(feature_matrix)
        distances, indices = neighbors_fit.kneighbors(feature_matrix)
        
        # Sort distances and find the "elbow"
        distances = np.sort(distances[:, k-1])
        
        # Simple heuristic: use 75th percentile of k-distances
        eps = np.percentile(distances, 75)
        
        return max(eps, 0.1)  # Minimum eps value
    
    def get_cluster_summaries(self, clustered_df: pd.DataFrame) -> Dict[int, Dict[str, Any]]:
        """Generate summaries for each cluster"""
        summaries = {}
        
        for cluster_id in clustered_df['cluster'].unique():
            cluster_data = clustered_df[clustered_df['cluster'] == cluster_id]
            
            # Basic statistics
            summary = {
                'size': len(cluster_data),
                'avg_amount': cluster_data['amount'].mean(),
                'total_value': cluster_data['amount'].sum(),
                'amount_range': (cluster_data['amount'].min(), cluster_data['amount'].max()),
                'avg_gpa': cluster_data['gpa_requirement'].mean(),
                'gpa_range': (cluster_data['gpa_requirement'].min(), cluster_data['gpa_requirement'].max())
            }
            
            # Most common category
            category_counts = cluster_data['category'].value_counts()
            summary['most_common_category'] = category_counts.index[0] if not category_counts.empty else "N/A"
            summary['category_distribution'] = category_counts.to_dict()
            
            # Most common demographics
            all_demographics = []
            for demo_list in cluster_data['target_demographics']:
                all_demographics.extend(demo_list)
            
            if all_demographics:
                from collections import Counter
                demo_counts = Counter(all_demographics)
                summary['most_common_demographics'] = dict(demo_counts.most_common(5))
            else:
                summary['most_common_demographics'] = {}
            
            # Deadline analysis
            try:
                deadline_dates = pd.to_datetime(cluster_data['deadline'])
                days_until = (deadline_dates - pd.Timestamp.now()).dt.days
                summary['avg_days_until_deadline'] = days_until.mean()
                summary['urgent_deadlines'] = (days_until <= 30).sum()
            except:
                summary['avg_days_until_deadline'] = None
                summary['urgent_deadlines'] = 0
            
            summaries[cluster_id] = summary
        
        return summaries
    
    def recommend_optimal_clusters(self, scholarships_df: pd.DataFrame, features: List[str]) -> Dict[str, Any]:
        """Recommend optimal number of clusters using silhouette analysis"""
        if len(scholarships_df) < 4:  # Need at least 4 points for meaningful clustering
            return {'recommended_clusters': 2, 'scores': {}, 'method': 'default'}
        
        feature_matrix = self._prepare_features(scholarships_df, features)
        if feature_matrix is None:
            return {'recommended_clusters': 2, 'scores': {}, 'method': 'default'}
        
        # Test different numbers of clusters
        max_clusters = min(10, len(scholarships_df) // 2)  # Don't exceed half the data points
        scores = {}
        
        for n in range(2, max_clusters + 1):
            try:
                kmeans = KMeans(n_clusters=n, random_state=42, n_init=10)
                cluster_labels = kmeans.fit_predict(feature_matrix)
                score = silhouette_score(feature_matrix, cluster_labels)
                scores[n] = score
            except:
                continue
        
        if not scores:
            return {'recommended_clusters': 2, 'scores': {}, 'method': 'default'}
        
        # Find the number of clusters with the highest silhouette score
        recommended_clusters = max(scores.keys(), key=lambda k: scores[k])
        
        return {
            'recommended_clusters': recommended_clusters,
            'scores': scores,
            'method': 'silhouette_analysis'
        }
    
    def visualize_clusters_2d(self, clustered_df: pd.DataFrame, feature_matrix: np.ndarray) -> Dict[str, Any]:
        """Prepare data for 2D visualization using PCA"""
        if feature_matrix.shape[1] < 2:
            return None
        
        # Apply PCA to reduce to 2 dimensions
        self.pca = PCA(n_components=2, random_state=42)
        coordinates_2d = self.pca.fit_transform(feature_matrix)
        
        # Create visualization data
        viz_data = {
            'x': coordinates_2d[:, 0],
            'y': coordinates_2d[:, 1],
            'cluster': clustered_df['cluster'].values,
            'title': clustered_df['title'].values,
            'amount': clustered_df['amount'].values,
            'category': clustered_df['category'].values,
            'explained_variance_ratio': self.pca.explained_variance_ratio_,
            'total_variance_explained': np.sum(self.pca.explained_variance_ratio_)
        }
        
        return viz_data
