import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Tuple, Optional, Any, Union
import traceback
from dataclasses import dataclass


@dataclass
class DataStats:
    """통계 정보를 저장하는 데이터 클래스"""
    total_participants: int = 0
    pass_rate: float = 0.0
    avg_score: float = 0.0
    dept_counts: Dict[str, int] = None
    grade_counts: Dict[str, int] = None
    level_counts: Dict[str, Any] = None
    std_dev: float = 0.0
    median: float = 0.0
    max_score: float = 0.0
    min_score: float = 0.0
    top10_avg: float = 0.0
    bottom10_avg: float = 0.0
    
    def __post_init__(self):
        if self.dept_counts is None:
            self.dept_counts = {}
        if self.grade_counts is None:
            self.grade_counts = {}
        if self.level_counts is None:
            self.level_counts = {}


class CodingTestMonitor:
    """코딩 테스트 모니터링 시스템의 핵심 클래스"""
    
    def __init__(self):
        """초기화 메서드"""
        self.columns = ['No.', '시험과목', '이메일', '합격여부', '총점', '등급(Lv.)', 
                       '학과', '학년', '학번']
        self.data = pd.DataFrame(columns=self.columns)
        self.test_rounds = []
        self.all_rounds_data = {}  # 모든 회차 데이터 저장
        self.target_department = '정보컴퓨터공학부'  # 집중 분석 대상 학과
        self.round_files = [
            '부산대학교 PCC_1회 응시 결과.csv',
            '부산대학교 PCC_2회 응시 결과.csv',
            '부산대학교 PCC_3회 응시 결과.csv',
            '부산대학교 PCC_4회 응시 결과.csv'
        ]
        
    def load_data(self, file) -> bool:
        """
        파일에서 데이터를 로드하고 데이터 타입을 변환합니다.
        
        Args:
            file: 업로드된 파일 객체
            
        Returns:
            bool: 로드 성공 여부
        """
        try:
            # 파일 로드
            if file.name.endswith('.csv'):
                df = pd.read_csv(file)
            elif file.name.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file)
            else:
                st.error("지원되지 않는 파일 형식입니다. CSV 또는 Excel 파일을 업로드해주세요.")
                return False
            
            # 필수 컬럼 확인
            missing_columns = [col for col in self.columns if col not in df.columns]
            if missing_columns:
                st.error(f"필수 컬럼이 누락되었습니다: {', '.join(missing_columns)}")
                return False
            
            # 데이터 타입 변환 및 정제
            self._clean_and_transform_data(df)
            
            self.data = df
            return True
            
        except Exception as e:
            st.error(f"파일 로드 중 오류 발생: {e}")
            return False
    
    def _clean_and_transform_data(self, df: pd.DataFrame) -> None:
        """
        데이터프레임의 타입 변환 및 정제를 수행합니다.
        
        Args:
            df: 정제할 데이터프레임
        """
        # 숫자형 컬럼 변환
        if 'No.' in df.columns:
            df['No.'] = pd.to_numeric(df['No.'], errors='coerce').astype('Int64')
        
        if '총점' in df.columns:
            df['총점'] = pd.to_numeric(df['총점'], errors='coerce').astype('float64')
        
        # 문자열 컬럼 변환
        string_columns = ['시험과목', '이메일', '합격여부', '등급(Lv.)', '학과', '학번']
        for col in string_columns:
            if col in df.columns:
                df[col] = df[col].astype(str)
        
        # 학년 특별 처리
        if '학년' in df.columns:
            df['학년'] = df['학년'].astype(str)
        
        # 결측값 처리
        df.fillna({
            '총점': 0,
            '학년': '1',
            'No.': 1
        }, inplace=True)
    
    def filter_data(self, filters: Dict[str, Any]) -> pd.DataFrame:
        """
        주어진 조건으로 데이터를 필터링합니다.
        
        Args:
            filters: 필터링 조건 딕셔너리
        
        Returns:
            pd.DataFrame: 필터링된 데이터프레임
        """
        try:
            filtered_data = self.data.copy()
            
            for key, value in filters.items():
                if value:  # 값이 존재하는 경우에만 필터링
                    if isinstance(value, list):
                        if value:  # 리스트가 비어있지 않은 경우에만
                            filtered_data = filtered_data[filtered_data[key].isin(value)]                            
                    else:
                        # 학년 필터링 시 데이터 타입 처리
                        if key == '학년':
                            # 데이터를 문자열로 변환하여 비교
                            filtered_data = filtered_data[filtered_data[key].astype(str) == str(value)]
                        else:
                            filtered_data = filtered_data[filtered_data[key] == value]
            
            return filtered_data
        
        except Exception as e:
            st.error(f"필터링 중 오류 발생: {e}")
            st.error(traceback.format_exc())
            return self.data
    
    def get_statistics(self, data: pd.DataFrame) -> DataStats:
        """
        기본 통계 정보를 계산합니다.
        
        Args:
            data: 통계를 계산할 데이터프레임
        
        Returns:
            DataStats: 통계 정보를 담은 객체
        """
        try:
            if data.empty:
                return DataStats()
            
            stats = DataStats(
                total_participants=len(data),
                pass_rate=(data['합격여부'] == '합격').mean() * 100,
                avg_score=data['총점'].mean(),
                dept_counts=data['학과'].value_counts().to_dict(),
                grade_counts=data['학년'].value_counts().to_dict(),
                level_counts=data['등급(Lv.)'].value_counts().to_dict()
            )
            return stats
            
        except Exception as e:
            st.error(f"통계 계산 중 오류 발생: {e}")
            st.error(traceback.format_exc())
            return DataStats()
    
    def calculate_advanced_statistics(self, data: pd.DataFrame) -> Dict[str, float]:
        """
        고급 통계 정보를 계산합니다.
        
        Args:
            data: 통계를 계산할 데이터프레임
        
        Returns:
            Dict[str, float]: 고급 통계 정보 딕셔너리
        """
        try:
            if data.empty:
                return {}
                
            stats = {
                '표준편차': data['총점'].std(),
                '중앙값': data['총점'].median(),
                '최고점수': data['총점'].max(),
                '최저점수': data['총점'].min(),
                '상위 10% 평균': data['총점'].nlargest(max(1, int(len(data)*0.1))).mean(),
                '하위 10% 평균': data['총점'].nsmallest(max(1, int(len(data)*0.1))).mean()
            }
            return stats
            
        except Exception as e:
            st.error(f"고급 통계 계산 중 오류 발생: {e}")
            st.error(traceback.format_exc())
            return {}
    
    # 시각화 메서드들
    def create_plot(self, plot_type: str, data: pd.DataFrame, **kwargs) -> go.Figure:
        """
        데이터 시각화 메서드를 선택하고 실행합니다.
        
        Args:
            plot_type: 시각화 유형
            data: 시각화할 데이터프레임
            **kwargs: 추가 매개변수
            
        Returns:
            go.Figure: Plotly 그래프 객체
        """
        plot_methods = {
            'score_distribution': self.create_score_distribution_plot,
            'department_average_score': self.create_department_average_score_plot,
            'department_pass_rate': self.create_department_pass_rate_plot,
            'subject_average_score': self.create_subject_average_score_plot,
            'subject_pass_rate': self.create_subject_pass_rate_plot,
            'grade_distribution': self.create_grade_distribution_plot,
            'performance_radar': self.create_performance_radar,
            'performance_heatmap': self.create_performance_heatmap,
        }
        
        if plot_type not in plot_methods:
            st.error(f"지원되지 않는 시각화 유형: {plot_type}")
            return go.Figure()
        
        try:
            return plot_methods[plot_type](data, **kwargs)
        except Exception as e:
            st.error(f"{plot_type} 시각화 중 오류 발생: {e}")
            st.error(traceback.format_exc())
            return go.Figure()
    
    def create_score_distribution_plot(self, data: pd.DataFrame, **kwargs) -> go.Figure:
        """점수 분포를 시각화합니다."""
        if data.empty:
            return go.Figure()
            
        fig = px.histogram(
            data, 
            x='총점', 
            title='점수 분포',
            labels={'총점': '점수', 'count': '학생 수'},
            color='합격여부',
            color_discrete_map={'합격': 'green', '불합격': 'red'}
        )
        return fig
    
    def create_department_average_score_plot(self, data: pd.DataFrame, **kwargs) -> go.Figure:
        """학과별 평균 점수를 시각화합니다."""
        if data.empty:
            return go.Figure()
            
        dept_scores = data.groupby('학과').agg({'총점': 'mean'}).reset_index()
        
        fig = px.bar(
            dept_scores, 
            x='학과', 
            y='총점',
            title='학과별 평균 점수',
            labels={'총점': '평균 점수', '학과': '학과'}
        )
        return fig
    
    def create_department_pass_rate_plot(self, data: pd.DataFrame, **kwargs) -> go.Figure:
        """학과별 합격률을 시각화합니다."""
        if data.empty:
            return go.Figure()
            
        dept_pass_rate = data.groupby('학과').agg(
            {'합격여부': lambda x: (x == '합격').mean() * 100}
        ).reset_index()
        
        fig = px.bar(
            dept_pass_rate, 
            x='학과', 
            y='합격여부',
            title='학과별 합격률',
            labels={'합격여부': '합격률(%)', '학과': '학과'}
        )
        return fig
    
    def create_subject_average_score_plot(self, data: pd.DataFrame, **kwargs) -> go.Figure:
        """과목별 평균 점수를 시각화합니다."""
        if data.empty:
            return go.Figure()
            
        subject_scores = data.groupby('시험과목').agg({'총점': 'mean'}).reset_index()
        
        fig = px.bar(
            subject_scores, 
            x='시험과목', 
            y='총점',
            title='과목별 평균 점수',
            labels={'총점': '평균 점수', '시험과목': '과목'}
        )
        return fig
    
    def create_subject_pass_rate_plot(self, data: pd.DataFrame, **kwargs) -> go.Figure:
        """과목별 합격률을 시각화합니다."""
        if data.empty:
            return go.Figure()
            
        subject_pass_rate = data.groupby('시험과목').agg(
            {'합격여부': lambda x: (x == '합격').mean() * 100}
        ).reset_index()
        
        fig = px.bar(
            subject_pass_rate, 
            x='시험과목', 
            y='합격여부',
            title='과목별 합격률',
            labels={'합격여부': '합격률(%)', '시험과목': '과목'}
        )
        return fig
    
    def create_grade_distribution_plot(self, data: pd.DataFrame, **kwargs) -> go.Figure:
        """등급 분포를 시각화합니다."""
        if data.empty:
            return go.Figure()
            
        grade_dist = data['등급(Lv.)'].value_counts().reset_index()
        grade_dist.columns = ['등급', '인원수']
        
        fig = px.pie(
            grade_dist, 
            values='인원수', 
            names='등급',
            title='등급별 분포',
            labels={'인원수': '인원수', '등급': '등급'},
            hover_data=['인원수']
        )
        fig.update_traces(textposition='inside', textinfo='percent+label+value')
        return fig
    
    def create_performance_radar(self, data: pd.DataFrame, department: str = None, **kwargs) -> go.Figure:
        """학과별 종합 성과 레이더 차트를 생성합니다."""
        if data.empty:
            return go.Figure()
            
        if department:
            dept_data = data[data['학과'] == department]
            if dept_data.empty:
                return go.Figure()
        else:
            dept_data = data
        
        metrics = {
            '평균점수': dept_data['총점'].mean() / 100,  # 정규화
            '합격률': (dept_data['합격여부'] == '합격').mean(),
            '상위등급비율': (dept_data['등급(Lv.)'].isin(['A', 'B'])).mean(),
            '참여율': len(dept_data) / len(data) if len(data) > 0 else 0,
            '개선도': 0.5  # 기본값, 시계열 데이터 필요
        }
        
        fig = go.Figure(data=go.Scatterpolar(
            r=list(metrics.values()),
            theta=list(metrics.keys()),
            fill='toself'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1]
                )),
            showlegend=False,
            title=f"{'전체' if not department else department} 종합 성과 분석"
        )
        
        return fig
    
    def create_score_box_plot(self) -> None:
        """정보컴퓨터공학부의 학년별 통계 정보를 표시합니다."""
        try:
            # 모든 회차 데이터 통합
            all_data = self._get_department_data(self.target_department)
            
            if all_data.empty:
                st.warning(f"{self.target_department} 데이터가 없습니다.")
                return
            
            # 학년을 정수로 변환
            all_data['학년'] = pd.to_numeric(all_data['학년'], errors='coerce')
            all_data = all_data.dropna(subset=['학년'])
            all_data['학년'] = all_data['학년'].astype(int)
            
            # 학년별 통계 계산 및 표시
            stats_data = self._calculate_grade_statistics(all_data)
            
            # DataFrame 생성 및 표시
            stats_df = pd.DataFrame(stats_data)
            
            # 학년별 통계 표시
            st.subheader(f'{self.target_department} 학년별 통계')
            st.dataframe(
                stats_df,
                column_config={
                    '학년': st.column_config.TextColumn('학년'),
                    '총인원': st.column_config.NumberColumn('총인원', help='전체 응시자 수'),
                    '합격인원': st.column_config.NumberColumn('합격인원', help='합격자 수'),
                    '불합격인원': st.column_config.NumberColumn('불합격인원', help='불합격자 수'),
                    '합격률(%)': st.column_config.TextColumn('합격률(%)', help='합격자 비율'),
                    '합격자평균': st.column_config.TextColumn('합격자평균', help='합격자들의 평균 점수')
                },
                hide_index=True,
                width=800
            )
            
            # 전체 통계 계산 및 표시
            self._display_total_statistics(all_data)
            
        except Exception as e:
            st.error(f"통계 정보 생성 중 오류 발생: {str(e)}")
            st.error(traceback.format_exc())
    
    def _calculate_grade_statistics(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """학년별 통계 정보를 계산합니다."""
        stats_data = []
        for grade in sorted(data['학년'].unique()):
            grade_data = data[data['학년'] == grade]
            total_students = len(grade_data)
            
            if total_students > 0:
                pass_data = grade_data[grade_data['합격여부'] == '합격']
                fail_data = grade_data[grade_data['합격여부'] == '불합격']
                
                pass_count = len(pass_data)
                fail_count = len(fail_data)
                pass_rate = (pass_count / total_students) * 100
                pass_avg = pass_data['총점'].mean() if not pass_data.empty else 0
                
                stats_data.append({
                    '학년': f'{grade}학년',
                    '총인원': total_students,
                    '합격인원': pass_count,
                    '불합격인원': fail_count,
                    '합격률(%)': f'{pass_rate:.1f}%',
                    '합격자평균': f'{pass_avg:.1f}점'
                })
        return stats_data
    
    def _display_total_statistics(self, data: pd.DataFrame) -> None:
        """전체 통계 정보를 계산하고 표시합니다."""
        total_students = len(data)
        total_pass = len(data[data['합격여부'] == '합격'])
        total_fail = len(data[data['합격여부'] == '불합격'])
        total_pass_rate = (total_pass / total_students) * 100 if total_students > 0 else 0
        total_pass_avg = data[data['합격여부'] == '합격']['총점'].mean() if total_pass > 0 else 0
        
        st.subheader('전체 통계')
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("총 인원", f"{total_students}명")
        with col2:
            st.metric("합격 인원", f"{total_pass}명")
        with col3:
            st.metric("불합격 인원", f"{total_fail}명")
        with col4:
            st.metric("전체 합격률", f"{total_pass_rate:.1f}%")
        with col5:
            st.metric("전체 합격자 평균", f"{total_pass_avg:.1f}점")
    
    def _get_department_data(self, department: str) -> pd.DataFrame:
        """특정 학과의 모든 회차 데이터를 통합하여 반환합니다."""
        all_data = pd.DataFrame()
        for round_num, round_data in self.all_rounds_data.items():
            round_data = round_data.copy()
            # 지정된 학과 데이터만 필터링
            dept_data = round_data[round_data['학과'] == department].copy()
            if not dept_data.empty:
                all_data = pd.concat([all_data, dept_data])
        return all_data
    
    # 회차 관련 메서드들
    def load_all_rounds_data(self, file_list: List[str] = None) -> bool:
        """
        모든 회차의 데이터를 로드합니다.
        
        Args:
            file_list: 로드할 파일 목록 (기본값: None, 내부 정의 파일 사용)
            
        Returns:
            bool: 로드 성공 여부
        """
        try:
            if file_list is None:
                file_list = self.round_files
                
            for file_name in file_list:
                try:
                    round_num = int(file_name.split('_')[1][0])
                    file = open(file_name, 'r')
                    df = pd.read_csv(file)
                    self._clean_and_transform_data(df)
                    self.all_rounds_data[round_num] = df
                except Exception as e:
                    st.warning(f"파일 '{file_name}' 로드 중 오류: {e}")
                    continue
                    
            return len(self.all_rounds_data) > 0
            
        except Exception as e:
            st.error(f"전체 회차 데이터 로드 중 오류 발생: {e}")
            st.error(traceback.format_exc())
            return False
    
    def create_performance_heatmap(self, data: pd.DataFrame = None, **kwargs) -> go.Figure:
        """모든 회차의 정보컴퓨터공학부 응시자 현황을 시각화합니다."""
        try:
            # 모든 회차 데이터 통합 및 준비
            all_data = self._prepare_performance_data()
            
            if all_data.empty:
                st.warning(f"{self.target_department} 데이터가 없습니다.")
                return go.Figure()
                
            # 회차별 합격/불합격 학생수 계산
            summary_data = all_data.groupby(['회차', '합격여부']).size().reset_index(name='학생수')
            
            # 전체 응시자수 계산
            total_data = all_data.groupby('회차').size().reset_index(name='전체')
            
            # 합격률 계산
            pass_rate_df = self._calculate_pass_rates(summary_data, total_data)
            
            return self._create_performance_chart(summary_data, total_data, pass_rate_df)
            
        except Exception as e:
            st.error(f"응시자 현황 시각화 중 오류 발생: {str(e)}")
            st.error(traceback.format_exc())
            return go.Figure()
    
    def _prepare_performance_data(self) -> pd.DataFrame:
        """성과 차트를 위한 데이터를 준비합니다."""
        all_data = pd.DataFrame()
        for round_num, round_data in self.all_rounds_data.items():
            round_data = round_data.copy()
            # 정보컴퓨터공학부 데이터만 필터링
            dept_data = round_data[round_data['학과'] == self.target_department].copy()
            if not dept_data.empty:
                dept_data['회차'] = round_num
                all_data = pd.concat([all_data, dept_data])
        return all_data
    
    def _calculate_pass_rates(self, summary_data: pd.DataFrame, total_data: pd.DataFrame) -> pd.DataFrame:
        """합격률을 계산합니다."""
        pass_rates = []
        for round_num in total_data['회차']:
            total = total_data[total_data['회차'] == round_num]['전체'].iloc[0]
            pass_count = summary_data[(summary_data['회차'] == round_num) & 
                                     (summary_data['합격여부'] == '합격')]['학생수']
            passed = pass_count.iloc[0] if not pass_count.empty else 0
            pass_rate = (passed / total) * 100 if total > 0 else 0
            pass_rates.append(pass_rate)
        
        # 합격률 데이터프레임 생성
        return pd.DataFrame({
            '회차': total_data['회차'],
            '합격률': pass_rates
        })
    
    def _create_performance_chart(self, summary_data: pd.DataFrame, 
                                 total_data: pd.DataFrame, 
                                 pass_rate_df: pd.DataFrame) -> go.Figure:
        """합격률 및 응시자 현황 차트를 생성합니다."""
        fig = go.Figure()
        
        # 합격자 막대 추가
        pass_data = summary_data[summary_data['합격여부'] == '합격']
        if not pass_data.empty:
            fig.add_trace(go.Bar(
                name='합격',
                x=pass_data['회차'],
                y=pass_data['학생수'],
                text=pass_data['학생수'].astype(str) + '명',
                textposition='inside',
                marker_color='green',
                yaxis='y'
            ))
        
        # 불합격자 막대 추가
        fail_data = summary_data[summary_data['합격여부'] == '불합격']
        if not fail_data.empty:
            fig.add_trace(go.Bar(
                name='불합격',
                x=fail_data['회차'],
                y=fail_data['학생수'],
                text=fail_data['학생수'].astype(str) + '명',
                textposition='inside',
                marker_color='red',
                yaxis='y'
            ))
        
        # 전체 응시자수 선 그래프 추가
        fig.add_trace(go.Scatter(
            name='전체 응시자',
            x=total_data['회차'],
            y=total_data['전체'],
            text=total_data['전체'].astype(str) + '명',
            textposition='top center',
            mode='lines+markers+text',
            marker=dict(size=12, color='blue'),
            line=dict(color='blue', width=3),
            yaxis='y'
        ))
        
        # 합격률 선 그래프 추가 (이중 축)
        fig.add_trace(go.Scatter(
            name='합격률',
            x=pass_rate_df['회차'],
            y=pass_rate_df['합격률'],
            text=[f'{rate:.1f}%' for rate in pass_rate_df['합격률']],
            textposition='top right',
            mode='lines+markers+text',
            marker=dict(size=12, color='orange'),
            line=dict(color='orange', width=3, dash='dot'),
            yaxis='y2'  # 이중 축 사용
        ))
        
        # 레이아웃 설정
        fig.update_layout(
            title=f'{self.target_department} 회차별 응시자 현황',
            xaxis=dict(
                title='회차',
                tickmode='array',
                ticktext=[f'{i}회차' for i in sorted(pass_rate_df['회차'].unique())],
                tickvals=sorted(pass_rate_df['회차'].unique())
            ),
            yaxis=dict(
                title=dict(
                    text='응시자 수 (명)',
                    font=dict(color='black')
                ),
                side='left',
                tickfont=dict(color='black')
            ),
            yaxis2=dict(
                title=dict(
                    text='합격률 (%)',
                    font=dict(color='orange')
                ),
                side='right',
                overlaying='y',
                showgrid=False,
                range=[0, 100],  # 합격률은 0-100% 범위로 설정
                tickfont=dict(color='orange')
            ),
            barmode='stack',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            height=600,
            width=1000
        )
        
        return fig
