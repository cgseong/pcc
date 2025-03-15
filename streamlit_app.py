import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import plotly.graph_objects as go
import numpy as np

class CodingTestMonitor:
    def __init__(self):
        self.columns = ['No.', '시험과목',  '이메일', '합격여부', '총점', '등급(Lv.)', 
                       '학과', '학년', '학번']
        self.data = pd.DataFrame(columns=self.columns)
        self.test_rounds = []
        self.all_rounds_data = {}  # 모든 회차 데이터 저장
    
    def load_data(self, file):
        """파일에서 데이터를 로드하고 데이터 타입을 변환합니다."""
        try:
            # 파일 로드
            if file.name.endswith('.csv'):
                df = pd.read_csv(file)
            elif file.name.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file)
            
            # 데이터 타입 변환
            # No. 컬럼을 정수형으로 변환
            if 'No.' in df.columns:
                df['No.'] = pd.to_numeric(df['No.'], errors='coerce').astype('Int64')
            
            # 총점을 float64로 변환
            if '총점' in df.columns:
                df['총점'] = pd.to_numeric(df['총점'], errors='coerce').astype('float64')
            
            # 학년을 문자열로 변환
            if '학년' in df.columns:
                df['학년'] = df['학년'].astype(str)
            
            # 문자열 컬럼들의 타입 변환
            string_columns = ['시험과목',  '이메일', '합격여부', '등급(Lv.)', '학과', '학번']
            for col in string_columns:
                if col in df.columns:
                    df[col] = df[col].astype(str)
            
            # 결측값 처리
            df = df.fillna({
                '총점': 0,
                '학년': '1',
                'No.': 1
            })
            
            self.data = df
            return True
            
        except Exception as e:
            st.error(f"파일 로드 중 오류 발생: {e}")
            return False
    
    def filter_data(self, filters):
        """주어진 조건으로 데이터를 필터링합니다."""
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
            return self.data
    
    def get_statistics(self, data):
        """기본 통계 정보를 계산합니다."""
        try:
            stats = {
                '총 응시자 수': len(data),
                '합격률': (data['합격여부'] == '합격').mean() * 100,
                '평균 점수': data['총점'].mean(),
                '학과별 응시자 수': data['학과'].value_counts().to_dict(),
                '학년별 응시자 수': data['학년'].value_counts().to_dict(),
                '등급별 분포': data['등급(Lv.)'].value_counts().to_dict()
            }
            return stats
        except Exception as e:
            st.error(f"통계 계산 중 오류 발생: {e}")
            return {
                '총 응시자 수': 0,
                '합격률': 0,
                '평균 점수': 0,
                '학과별 응시자 수': {},
                '학년별 응시자 수': {},
                '등급별 분포': {}
            }
    
    def create_score_distribution_plot(self, data):
        """점수 분포를 시각화합니다."""
        try:
            fig = px.histogram(data, x='총점', title='점수 분포',
                             labels={'총점': '점수', 'count': '학생 수'},
                             color='합격여부',
                             color_discrete_map={'합격': 'green', '불합격': 'red'})
            return fig
        except Exception as e:
            st.error(f"점수 분포 시각화 중 오류 발생: {e}")
            return go.Figure()
    
    def create_department_average_score_plot(self, data):
        """학과별 평균 점수를 시각화합니다."""
        try:
            dept_scores = data.groupby('학과').agg({'총점': 'mean'}).reset_index()
            
            fig = px.bar(dept_scores, x='학과', y='총점',
                        title='학과별 평균 점수',
                        labels={'총점': '평균 점수', '학과': '학과'})
            return fig
        except Exception as e:
            st.error(f"학과별 평균 점수 시각화 중 오류 발생: {e}")
            return go.Figure()

    def create_department_pass_rate_plot(self, data):
        """학과별 합격률을 시각화합니다."""
        try:
            dept_pass_rate = data.groupby('학과').agg({'합격여부': lambda x: (x == '합격').mean() * 100}).reset_index()
            
            fig = px.bar(dept_pass_rate, x='학과', y='합격여부',
                        title='학과별 합격률',
                        labels={'합격여부': '합격률(%)', '학과': '학과'})
            return fig
        except Exception as e:
            st.error(f"학과별 합격률 시각화 중 오류 발생: {e}")
            return go.Figure()

    def create_subject_average_score_plot(self, data):
        """과목별 평균 점수를 시각화합니다."""
        try:
            subject_scores = data.groupby('시험과목').agg({'총점': 'mean'}).reset_index()
            
            fig = px.bar(subject_scores, x='시험과목', y='총점',
                        title='과목별 평균 점수',
                        labels={'총점': '평균 점수', '시험과목': '과목'})
            return fig
        except Exception as e:
            st.error(f"과목별 평균 점수 시각화 중 오류 발생: {e}")
            return go.Figure()

    def create_subject_pass_rate_plot(self, data):
        """과목별 합격률을 시각화합니다."""
        try:
            subject_pass_rate = data.groupby('시험과목').agg({'합격여부': lambda x: (x == '합격').mean() * 100}).reset_index()
            
            fig = px.bar(subject_pass_rate, x='시험과목', y='합격여부',
                        title='과목별 합격률',
                        labels={'합격여부': '합격률(%)', '시험과목': '과목'})
            return fig
        except Exception as e:
            st.error(f"과목별 합격률 시각화 중 오류 발생: {e}")
            return go.Figure()
    
    def create_grade_distribution_plot(self, data):
        """등급 분포를 시각화합니다."""
        try:
            grade_dist = data['등급(Lv.)'].value_counts().reset_index()
            grade_dist.columns = ['등급', '인원수']
            
            fig = px.pie(grade_dist, values='인원수', names='등급',
                        title='등급별 분포',
                        labels={'인원수': '인원수', '등급': '등급'},
                        hover_data=['인원수'])
            fig.update_traces(textposition='inside', textinfo='percent+label+value')
            return fig
        except Exception as e:
            st.error(f"등급 분포 시각화 중 오류 발생: {e}")
            return go.Figure()
    
    def create_performance_heatmap(self, data):
        """학과별/학년별 성과 히트맵을 생성합니다."""
        try:
            # 학과-학년별 평균 점수 계산
            heatmap_data = data.pivot_table(
                values='총점',
                index='학과',
                columns='학년',
                aggfunc='mean'
            ).round(2)
            
            fig = go.Figure(data=go.Heatmap(
                z=heatmap_data.values,
                x=heatmap_data.columns,
                y=heatmap_data.index,
                text=heatmap_data.values.round(1),
                texttemplate='%{text}',
                textfont={"size": 10},
                hoverongaps=False,
                colorscale='RdYlGn'
            ))
            
            fig.update_layout(
                title='학과-학년별 평균 점수 분포',
                xaxis_title='학년',
                yaxis_title='학과'
            )
            
            return fig
        except Exception as e:
            st.error(f"히트맵 생성 중 오류 발생: {e}")
            return go.Figure()
    
    def create_performance_radar(self, data, department=None):
        """학과별 종합 성과 레이더 차트를 생성합니다."""
        try:
            if department:
                dept_data = data[data['학과'] == department]
            else:
                dept_data = data
            
            metrics = {
                '평균점수': dept_data['총점'].mean() / 100,  # 정규화
                '합격률': (dept_data['합격여부'] == '합격').mean(),
                '상위등급비율': (dept_data['등급(Lv.)'].isin(['A', 'B'])).mean(),
                '참여율': len(dept_data) / len(data),
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
        except Exception as e:
            st.error(f"레이더 차트 생성 중 오류 발생: {e}")
            return go.Figure()
        
    def create_score_box_plot(self, data):
        """학과별 점수 분포 박스플롯을 생성합니다."""
        try:
            fig = px.box(data, x='학과', y='총점',
                        title='학과별 점수 분포',
                        points='all',  # 모든 데이터 포인트 표시
                        color='합격여부')
            
            fig.update_layout(
                xaxis_title='학과',
                yaxis_title='점수'
            )
            
            return fig
        except Exception as e:
            st.error(f"박스플롯 생성 중 오류 발생: {e}")
            return go.Figure()

    def calculate_advanced_statistics(self, data):
        """고급 통계 정보를 계산합니다."""
        try:
            stats = {
                '표준편차': data['총점'].std(),
                '중앙값': data['총점'].median(),
                '최고점수': data['총점'].max(),
                '최저점수': data['총점'].min(),
                '상위 10% 평균': data['총점'].nlargest(int(len(data)*0.1)).mean(),
                '하위 10% 평균': data['총점'].nsmallest(int(len(data)*0.1)).mean()
            }
            return stats
        except Exception as e:
            st.error(f"고급 통계 계산 중 오류 발생: {e}")
            return {}

    def load_all_rounds_data(self):
        """모든 회차의 데이터를 로드합니다."""
        try:
            for round_file in [
                '부산대학교 PCC_1회 응시 결과.csv',
                '부산대학교 PCC_2회 응시 결과.csv',
                '부산대학교 PCC_3회 응시 결과.csv',
                '부산대학교 PCC_4회 응시 결과.csv'
            ]:
                round_num = int(round_file.split('_')[1][0])
                file = open(round_file, 'r')
                df = pd.read_csv(file)
                self.all_rounds_data[round_num] = df
            return True
        except Exception as e:
            st.error(f"전체 회차 데이터 로드 중 오류 발생: {e}")
            return False

    def get_student_progress(self, email):
        """특정 학생의 회차별 성과를 추적합니다."""
        try:
            progress_data = []
            for round_num, data in self.all_rounds_data.items():
                student_data = data[data['이메일'] == email]
                if not student_data.empty:
                    progress_data.append({
                        '회차': round_num,
                        '총점': student_data['총점'].iloc[0],
                        '합격여부': student_data['합격여부'].iloc[0],
                        '등급': student_data['등급(Lv.)'].iloc[0]
                    })
            return pd.DataFrame(progress_data)
        except Exception as e:
            st.error(f"학생 진행 데이터 추출 중 오류 발생: {e}")
            return pd.DataFrame()

    def get_multiple_test_students(self):
        """2회 이상 테스트를 수행한 학생들의 이메일 목록을 반환합니다."""
        try:
            # 각 학생별 응시 횟수 계산
            student_counts = {}
            for data in self.all_rounds_data.values():
                for email in data['이메일'].unique():
                    student_counts[email] = student_counts.get(email, 0) + 1
            
            # 2회 이상 응시한 학생들만 필터링
            multiple_test_students = [
                email for email, count in student_counts.items() 
                if count >= 2
            ]
            
            # 학생 정보 가져오기 (이메일, 학과, 학번)
            student_info = []
            for email in multiple_test_students:
                # 가장 최근 회차의 데이터에서 학생 정보 가져오기
                for round_data in reversed(self.all_rounds_data.values()):
                    student_data = round_data[round_data['이메일'] == email]
                    if not student_data.empty:
                        student_info.append({
                            '이메일': email,
                            '학과': student_data['학과'].iloc[0],
                            '학번': student_data['학번'].iloc[0],
                            '응시횟수': student_counts[email]
                        })
                        break
            
            return pd.DataFrame(student_info)
        except Exception as e:
            st.error(f"다중 응시자 목록 생성 중 오류 발생: {e}")
            return pd.DataFrame()
        
    def create_student_progress_plots(self, email):
        """학생의 회차별 성과를 시각화합니다."""
        try:
            progress_df = self.get_student_progress(email)
            if progress_df.empty:
                return None, None, None

            # 점수 추이 그래프
            score_fig = go.Figure()
            score_fig.add_trace(go.Scatter(
                x=progress_df['회차'],
                y=progress_df['총점'],
                mode='lines+markers+text',
                name='점수',
                text=progress_df['총점'].round(1),
                textposition='top center',
                line=dict(color='blue'),
                marker=dict(
                    color=['green' if x == '합격' else 'red' for x in progress_df['합격여부']],
                    size=12
                )
            ))
            score_fig.update_layout(
                title='회차별 점수 추이',
                **xaxis=dict(
                title='회차',
                tickmode='array',
                ticktext=progress_df['회차'].astype(int),
                tickvals=progress_df['회차'],
                dtick=1)  # 정수,
                yaxis_title='점수',
                showlegend=False
            )

            # 등급 변화 그래프
            grade_fig = go.Figure()
            grade_fig.add_trace(go.Scatter(
                x=progress_df['회차'],
                y=progress_df['등급'],
                mode='lines+markers+text',
                text=progress_df['등급'],
                textposition='top center',
                line=dict(color='purple'),
                marker=dict(size=12)
            ))
            grade_fig.update_layout(
                title='회차별 등급 변화',
                xaxis=dict(
                title='회차',
                tickmode='array',
                ticktext=progress_df['회차'].astype(int),
                tickvals=progress_df['회차'],
                dtick=1  # 정수 간격으로 표시
            ),
                yaxis_title='등급',
                showlegend=False
            )

            # 성과 요약 테이블
            summary_df = pd.DataFrame({
                '지표': ['응시 횟수', '평균 점수', '최고 점수', '최저 점수', '합격 횟수'],
                '값': [
                    len(progress_df),
                    progress_df['총점'].mean().round(1),
                    progress_df['총점'].max().round(1),
                    progress_df['총점'].min().round(1),
                    (progress_df['합격여부'] == '합격').sum()
                ]
            })

            return score_fig, grade_fig, summary_df
        except Exception as e:
            st.error(f"학생 성과 시각화 중 오류 발생: {e}")
            return None, None, None



def main():
    st.set_page_config(page_title="닥코(닥치고 코딩)", layout="wide")
    
    st.title("코딩 역량 테스트")
    
    # 모니터링 객체 생성
    monitor = CodingTestMonitor()
    
    # 파일 업로드
    st.sidebar.header("데이터 업로드")
    uploaded_file = st.sidebar.selectbox(
        "테스트 결과 파일 선택",
        [
            '부산대학교 PCC_1회 응시 결과.csv',
            '부산대학교 PCC_2회 응시 결과.csv',
            '부산대학교 PCC_3회 응시 결과.csv',
            '부산대학교 PCC_4회 응시 결과.csv'
        ]
    )

    if uploaded_file:
        try:
            file = open(uploaded_file, 'r')
            if monitor.load_data(file):
                st.sidebar.success("데이터 로드 완료!")
        except Exception as e:
            st.error(f"파일 로드 중 오류 발생: {e}")
    
    if not monitor.data.empty:
        try:
            # 필터링 옵션
            st.sidebar.header("데이터 필터링")
            
            # 학과 필터
            departments = sorted(monitor.data['학과'].unique().tolist())
            selected_dept = st.sidebar.multiselect("학과 선택 (다중 선택 가능)", departments)
            
            # 학년 필터
            years = [''] + sorted(monitor.data['학년'].unique().tolist())
            selected_year = st.sidebar.selectbox("학년 선택", years)
            
            # 합격여부 필터
            pass_status = [''] + sorted(monitor.data['합격여부'].unique().tolist())
            selected_status = st.sidebar.selectbox("합격여부 선택", pass_status)
            
            # 등급 필터
            levels = [''] + sorted(monitor.data['등급(Lv.)'].unique().tolist())
            selected_level = st.sidebar.selectbox("등급 선택", levels)
            
            # 시험과목 필터
            subjects = [''] + sorted(monitor.data['시험과목'].unique().tolist())
            selected_subject = st.sidebar.selectbox("시험과목 선택", subjects)
            
            # 필터 적용
            filters = {
                '학과': selected_dept,
                '학년': selected_year,
                '합격여부': selected_status,
                '등급(Lv.)': selected_level,
                '시험과목': selected_subject
            }
            
            # 빈 값 제거
            filters = {k: v for k, v in filters.items() if v}
            
            filtered_data = monitor.filter_data(filters)
            
            # 기본 통계 표시
            st.header("기본 통계")
            stats = monitor.get_statistics(filtered_data)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("총 응시자 수", f"{stats['총 응시자 수']}명")
            with col2:
                st.metric("합격률", f"{stats['합격률']:.1f}%")
            with col3:
                st.metric("평균 점수", f"{stats['평균 점수']:.1f}점")
            
            # 시각화
            st.header("데이터 시각화")
            
            # 2x2 그리드로 차트 배치
            col1, col2 = st.columns(2)
            
            with col1:
                st.plotly_chart(monitor.create_score_distribution_plot(filtered_data),
                               use_container_width=True)
                st.plotly_chart(monitor.create_department_average_score_plot(filtered_data),
                               use_container_width=True)
                st.plotly_chart(monitor.create_department_pass_rate_plot(filtered_data),
                               use_container_width=True)
            
            with col2:
                st.plotly_chart(monitor.create_subject_average_score_plot(filtered_data),
                               use_container_width=True)
                st.plotly_chart(monitor.create_subject_pass_rate_plot(filtered_data),
                               use_container_width=True)
                st.plotly_chart(monitor.create_grade_distribution_plot(filtered_data),
                               use_container_width=True)
            
            # 데이터 테이블 표시
            st.header("상세 데이터")
            st.dataframe(filtered_data)
            
            # 데이터 다운로드 버튼
            if st.button("필터링된 데이터 다운로드"):
                output = pd.ExcelWriter('filtered_test_results.xlsx', engine='openpyxl')
                filtered_data.to_excel(output, index=False)
                output.close()
                
                with open('filtered_test_results.xlsx', 'rb') as f:
                    st.download_button(
                        label="Excel 파일 다운로드",
                        data=f,
                        file_name="filtered_test_results.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
            # 고급 분석 섹션
            st.header("고급 분석")
            
            # 탭 생성
            tab1, tab2, tab3 = st.tabs(["성과 분포", "상세 통계", "종합 분석"])
            
            with tab1:
                col1, col2 = st.columns(2)
                with col1:
                    # 히트맵 표시
                    heatmap_fig = monitor.create_performance_heatmap(filtered_data)
                    st.plotly_chart(heatmap_fig, use_container_width=True)
                
                with col2:
                    # 박스플롯 표시
                    box_fig = monitor.create_score_box_plot(filtered_data)
                    st.plotly_chart(box_fig, use_container_width=True)
            
            with tab2:
                # 고급 통계 정보 표시
                advanced_stats = monitor.calculate_advanced_statistics(filtered_data)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("표준편차", f"{advanced_stats.get('표준편차', 0):.1f}")
                    st.metric("중앙값", f"{advanced_stats.get('중앙값', 0):.1f}")
                with col2:
                    st.metric("최고점수", f"{advanced_stats.get('최고점수', 0):.1f}")
                    st.metric("최저점수", f"{advanced_stats.get('최저점수', 0):.1f}")
                with col3:
                    st.metric("상위 10% 평균", f"{advanced_stats.get('상위 10% 평균', 0):.1f}")
                    st.metric("하위 10% 평균", f"{advanced_stats.get('하위 10% 평균', 0):.1f}")
            
            with tab3:
                # 전체 레이더 차트
                radar_fig = monitor.create_performance_radar(filtered_data)
                st.plotly_chart(radar_fig, use_container_width=True)
                
                # 학과별 레이더 차트
                selected_dept = st.selectbox(
                    "학과 선택",
                    options=sorted(filtered_data['학과'].unique())
                )
                if selected_dept:
                    dept_radar_fig = monitor.create_performance_radar(filtered_data, selected_dept)
                    st.plotly_chart(dept_radar_fig, use_container_width=True)
                    
            st.header("학생별 성과 분석")
            
            # 전체 회차 데이터 로드
            if monitor.load_all_rounds_data():
                # 2회 이상 응시한 학생 목록 가져오기
                multiple_test_students = monitor.get_multiple_test_students()
                
                if not multiple_test_students.empty:
                    # 학생 선택을 위한 데이터프레임 표시
                    st.subheader("2회 이상 응시자 목록")
                    st.dataframe(
                        multiple_test_students,
                        column_config={
                            "이메일": "이메일",
                            "학과": "학과",
                            "학번": "학번",
                            "응시횟수": st.column_config.NumberColumn(
                                "응시횟수",
                                help="전체 응시 횟수"
                            )
                        },
                        hide_index=True
                    )
                    
                    # 학생 선택
                    selected_email = st.selectbox(
                        "분석할 학생 선택",
                        options=multiple_test_students['이메일'].tolist(),
                        format_func=lambda x: f"{x} ({multiple_test_students[multiple_test_students['이메일']==x]['학과'].iloc[0]} - {multiple_test_students[multiple_test_students['이메일']==x]['학번'].iloc[0]})"
                    )
                    
                    if selected_email:
                        score_fig, grade_fig, summary_df = monitor.create_student_progress_plots(selected_email)
                        
                        if score_fig and grade_fig and summary_df is not None:
                            # 성과 요약 표시
                            st.subheader("성과 요약")
                            st.dataframe(summary_df, hide_index=True)
                            
                            # 그래프 표시
                            col1, col2 = st.columns(2)
                            with col1:
                                st.plotly_chart(score_fig, use_container_width=True)
                            with col2:
                                st.plotly_chart(grade_fig, use_container_width=True)
                            
                            # 상세 데이터 표시
                            st.subheader("상세 회차별 데이터")
                            progress_data = monitor.get_student_progress(selected_email)
                            st.dataframe(progress_data)
                else:
                    st.warning("2회 이상 응시한 학생이 없습니다.")
                    
        except Exception as e:
            st.error(f"데이터 처리 중 오류 발생: {e}")
            st.info("데이터 형식을 확인해주세요.")
    
    
    else:
        st.warning("업로드된 파일에 데이터가 없습니다.")

if __name__ == "__main__":
    main()
