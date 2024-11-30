import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import plotly.graph_objects as go
import numpy as np

class CodingTestMonitor:
    def __init__(self):
        self.columns = ['No.', '시험과목', '이름', '이메일', '합격여부', '총점', '등급(Lv.)', 
                       '학과', '학년', '학번']
        self.data = pd.DataFrame(columns=self.columns)
    
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
            string_columns = ['시험과목', '이름', '이메일', '합격여부', '등급(Lv.)', '학과', '학번']
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
        
        except Exception as e:
            st.error(f"데이터 처리 중 오류 발생: {e}")
            st.info("데이터 형식을 확인해주세요.")
    else:
        st.warning("업로드된 파일에 데이터가 없습니다.")

if __name__ == "__main__":
    main()
